from langchain_google_genai import ChatGoogleGenerativeAI
import pandas as pd
import json
import streamlit as st

from utils import get_data_profile
from agents.guardian import run_guardian_query
from agents.sage import get_sage_interpretation
from agents.artisan import create_static_plot

def handle_general_conversation(llm: ChatGoogleGenerativeAI, user_query: str) -> str:
    """
    Lida com conversas gerais, saudações e perguntas não relacionadas a dados.
    """
    prompt = f"""Você é JEDI, um assistente de análise de dados temático de Star Wars.
Responda à pergunta do usuário de forma breve, amigável e dentro do tema.

Pergunta do usuário: "{user_query}"
Sua resposta:
"""
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        return f"A Força está perturbada. Não consegui processar a conversa. Erro: {str(e)}"

def run_jedi_council(llm: ChatGoogleGenerativeAI, df: pd.DataFrame, user_query: str, record_thoughts: bool = False):
    """
    Executa a orquestração do Conselho Jedi com esclarecimento com estado.

    Fluxo de Lógica:
    1. Verifica se há uma pergunta de esclarecimento pendente e a trata.
    2. Se não, usa um LLM para classificar a intenção do usuário e escolher uma ferramenta (Guardian, Visualizer, GeneralConversation).
    3. Para tarefas de dados/visualização, usa um LLM para atuar como um 'Consultor', avaliando a ambiguidade da pergunta ou sugerindo uma abordagem melhor.
    4. Se a pergunta for ambígua, retorna uma pergunta de esclarecimento e salva o estado.
    5. Se a pergunta for clara, executa a ferramenta apropriada.
    6. Envia o resultado da ferramenta para o Sábio para uma interpretação final em linguagem natural.
    7. Retorna um dicionário contendo a resposta final, o caminho para qualquer artefato e o log de pensamentos (Diário de Bordo).
    """
    log_entries = []
    def log(message):
        if record_thoughts:
            log_entries.append(message)

    if "pending_clarification" in st.session_state and st.session_state.pending_clarification:
        pending_data = st.session_state.pending_clarification
        original_query = pending_data["original_query"]
        intended_tool = pending_data["intended_tool"]
        
        log("🤔 **Pensamento:** O usuário respondeu a uma pergunta de esclarecimento. Combinando o contexto.")
        clarified_query = f"A pergunta original era '{original_query}'. O usuário agora esclareceu com: '{user_query}'. Execute a tarefa original com este novo esclarecimento."
        
        st.session_state.pending_clarification = None
        
        log(f"🎬 **Ação:** Acionando a ferramenta '{intended_tool}' com a consulta esclarecida.")
        tool_response = {}
        if intended_tool == "DataGuardian":
            tool_response = run_guardian_query(llm, df, clarified_query, record_thoughts)
        elif intended_tool == "Visualizer":
            tool_response = create_static_plot(llm, df, clarified_query, record_thoughts)
        
        tool_result = tool_response.get("result", "")
        specialist_thoughts = tool_response.get("thoughts", "")
        if record_thoughts and specialist_thoughts:
            log(f"--- Início do Log Detalhado de {intended_tool} ---")
            log(f"```\n{specialist_thoughts}\n```")
            log(f"--- Fim do Log Detalhado de {intended_tool} ---")

        log("🤔 **Pensamento:** Enviando o resultado para o Sábio fazer a interpretação final.")
        final_answer = get_sage_interpretation(llm, tool_result, clarified_query)
        artifact_path = tool_result if intended_tool == "Visualizer" else None
        return {"text_answer": final_answer, "artifact_path": artifact_path, "thoughts": log_entries}

    tools = [
        {"name": "DataGuardian", "description": "Útil para responder a perguntas que exigem análise de dados brutos, cálculos ou estatísticas."},
        {"name": "Visualizer", "description": "Útil para criar uma visualização de dados, um gráfico ou um plot."},
        {"name": "GeneralConversation", "description": "Use para saudações ou perguntas gerais que não são sobre os dados."}
    ]

    try:
        df_profile = get_data_profile(df)
        tools_json = json.dumps(tools, indent=2, ensure_ascii=False)
        tool_selection_prompt = f'''Sua tarefa é selecionar a ferramenta mais apropriada para responder à pergunta do usuário. Você DEVE seguir estas regras:
1. Analise o Perfil do DataFrame abaixo. Se a pergunta do usuário mencionar qualquer nome de coluna ou se referir a características dos dados (como 'colunas', 'linhas', 'tipos de dados', 'distribuição', etc.), você DEVE escolher 'DataGuardian' ou 'Visualizer'.
2. Apenas se a pergunta for uma saudação ou claramente não relacionada aos dados, escolha 'GeneralConversation'.

### Perfil do DataFrame
{df_profile}

Ferramentas disponíveis:
{tools_json}

Pergunta do usuário: "{user_query}"

Ferramenta selecionada (JSON):
'''
        
        log("🤔 **Pensamento:** Analisando a intenção do usuário para selecionar a ferramenta correta.")

        # Lógica de Curto-Circuito para forçar a seleção da ferramenta correta
        query_lower = user_query.lower()
        viz_keywords = ['gráfico', 'plot', 'visualize', 'visualização', 'histograma', 'barras', 'pizza', 'scatterplot', 'boxplot']
        data_keywords = ['coluna', 'colunas', 'dado', 'dados', 'tipo', 'tipos', 'distribuição', 'correlação', 'média', 'mediana']

        tool_name = ""
        if any(keyword in query_lower for keyword in viz_keywords):
            tool_name = "Visualizer"
            log("💡 **Curto-circuito:** Pergunta de visualização detectada. Forçando o uso do Visualizer.")
        elif any(keyword in query_lower for keyword in data_keywords) or any(col.lower() in query_lower for col in df.columns):
            tool_name = "DataGuardian"
            log("💡 **Curto-circuito:** Pergunta de análise de dados detectada. Forçando o uso do DataGuardian.")
        
        # Se nenhuma palavra-chave foi detectada, use o LLM para classificação
        if not tool_name:
            log("🤔 **Pensamento:** Nenhuma palavra-chave detectada. Usando LLM para classificação de intenção.")
            response = llm.invoke(tool_selection_prompt)
            tool_choice_str = response.content.strip()
            try:
                if tool_choice_str.startswith("```json"):
                    tool_choice_str = tool_choice_str[7:-3].strip()
                tool_choice = json.loads(tool_choice_str)
                if isinstance(tool_choice, dict):
                    tool_name = tool_choice.get('tool_name')
            except (json.JSONDecodeError, AttributeError):
                if "DataGuardian" in tool_choice_str:
                    tool_name = "DataGuardian"
                elif "Visualizer" in tool_choice_str:
                    tool_name = "Visualizer"
                elif "GeneralConversation" in tool_choice_str:
                    tool_name = "GeneralConversation"
            if not tool_name:
                tool_name = "GeneralConversation"
        log(f"🤔 **Pensamento:** A intenção parece ser '{tool_name}'.")

        if tool_name == "GeneralConversation":
            log("🎬 **Ação:** A pergunta é uma conversa geral. Acionando o modo de conversação.")
            response_text = handle_general_conversation(llm, user_query)
            return {"text_answer": response_text, "artifact_path": None, "thoughts": log_entries}

        guidance_prompt = f"""
        Você é um consultor de ciência de dados sênior. A pergunta do usuário é: '{user_query}'. A ferramenta selecionada é '{tool_name}'.
        Sua tarefa é dupla:
        1. Avalie se a pergunta é ambígua (ex: "mostre a distribuição" sem especificar o tipo de gráfico).
        2. Mesmo que clara, avalie se existe uma abordagem melhor (ex: sugerir um gráfico de barras em vez de um de pizza para duas categorias).

        Se a pergunta for clara e ideal, responda com JSON: {{"action": "proceed"}}.
        Se for ambígua ou puder ser melhorada, formule uma sugestão/pergunta e responda com JSON: {{"action": "clarify", "response": "Sua sugestão ou pergunta aqui."}}.

        Exemplo (Sugestão): Pergunta: "gráfico de pizza da coluna 'Class'". Resposta: {{"action": "clarify", "response": "Um gráfico de pizza pode ser usado, mas para comparar apenas duas categorias como na coluna 'Class', um gráfico de barras costuma ser mais claro e eficaz. Você gostaria que eu gerasse um gráfico de barras em vez disso?"}}
        Exemplo (Clara): Pergunta: "crie um histograma da coluna 'Amount'". Resposta: {{"action": "proceed"}}

        Sua avaliação para a pergunta "{user_query}":
        """
        log("🤔 **Pensamento:** Verificando se a pergunta é clara ou se posso sugerir uma abordagem melhor.")
        guidance_response = llm.invoke(guidance_prompt)
        guidance_check = json.loads(guidance_response.content.strip().replace("```json", "").replace("```", ""))

        if guidance_check.get("action") == "clarify":
            log(f"🎬 **Ação:** A pergunta é ambígua/pode ser melhorada. Pedindo esclarecimento ao usuário.")
            st.session_state.pending_clarification = {"original_query": user_query, "intended_tool": tool_name}
            return {"text_answer": guidance_check["response"], "artifact_path": None, "thoughts": log_entries}
        
        log(f"🤔 **Pensamento:** A pergunta é clara. Acionando a ferramenta '{tool_name}'.")
        log(f"🎬 **Ação:** Acionando a ferramenta `{tool_name}`.")
        tool_response = {}
        if tool_name == "DataGuardian":
            tool_response = run_guardian_query(llm, df, user_query, record_thoughts)
        elif tool_name == "Visualizer":
            tool_response = create_static_plot(llm, df, user_query, record_thoughts)
        
        tool_result = tool_response.get("result", "")
        specialist_thoughts = tool_response.get("thoughts", "")

        if record_thoughts and specialist_thoughts:
            log(f"--- Início do Log Detalhado de {tool_name} ---")
            log(f"```\n{specialist_thoughts}\n```")
            log(f"--- Fim do Log Detalhado de {tool_name} ---")

        log(f"🔍 **Observação:** A ferramenta '{tool_name}' retornou um resultado.")

        log("🤔 **Pensamento:** Enviando o resultado para o Sábio fazer a interpretação final.")
        log("🎬 **Ação:** Acionando a ferramenta `DataSage`.")
        final_answer = get_sage_interpretation(llm, tool_result, user_query)
        artifact_path = tool_result if tool_name == "Visualizer" else None
        return {"text_answer": final_answer, "artifact_path": artifact_path, "thoughts": log_entries}

    except Exception as e:
        return {"text_answer": f"O Conselho Jedi encontrou uma perturbação na Força. Um erro crítico ocorreu: {str(e)}", "artifact_path": None, "thoughts": log_entries}