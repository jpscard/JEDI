# --- Importações Essenciais ---
import streamlit as st
import pandas as pd
import os
import uuid
import shutil
import io
import datetime
import docx
from docx.shared import Inches
from contextlib import redirect_stdout
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.llms import Ollama
from utils import (
    get_ollama_models,
    get_gemini_models,
    parse_agent_thoughts,
    display_formatted_thoughts
)

def generate_docx_report(pinned_items, user_name):
    """Gera um relatório DOCX a partir dos itens pinados."""
    doc = docx.Document()
    doc.add_heading('Relatório JEDI', 0)
    doc.add_paragraph(f"Gerado por: {user_name}")
    doc.add_paragraph(f"Data: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    doc.add_paragraph("---_---")

    for item in pinned_items:
        doc.add_heading(f"Pergunta: {item['user_prompt']}", level=1)
        doc.add_paragraph(f"({item['timestamp']})")
        doc.add_heading("Resposta do Agente:", level=2)
        doc.add_paragraph(item['content'])
        if item.get("image") and os.path.exists(item["image"]):
            try:
                doc.add_picture(item["image"], width=Inches(6.0))
            except Exception as e:
                doc.add_paragraph(f"(Erro ao adicionar imagem: {e})")
        if item.get("thoughts"):
            doc.add_heading("Pensamentos do Agente:", level=3)
            for thought_step in item['thoughts']:
                doc.add_paragraph(f"- {thought_step['type']}: {thought_step['content']}")
        doc.add_paragraph("---_---")

    bio = io.BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def main_app():
    """A aplicação principal de EDA."""
    plots_dir = "temp_plots"

    def _pin_item(message):
        item_id = f"message-{message['timestamp']}-{hash(message['content'])}"
        
        for i, pinned_item in enumerate(st.session_state.pinned_items):
            if pinned_item.get("id") == item_id:
                st.session_state.pinned_items.pop(i)
                st.toast("Item despinado do relatório!", icon="📌")
                return

        user_prompt = ""
        if len(st.session_state.messages) > 1:
            # Assumindo que a mensagem anterior é a do usuário
            if st.session_state.messages[-1]["role"] == "assistant":
                 user_prompt = st.session_state.messages[-2]["content"]

        pinned_data = {
            "id": item_id,
            "role": "assistant",
            "content": message['content'],
            "timestamp": message['timestamp'],
            "image": message.get("image"),
            "thoughts": message.get("thoughts"),
            "user_prompt": user_prompt
        }
        st.session_state.pinned_items.append(pinned_data)
        st.toast("Item pinado para o relatório!", icon="✅")

    @st.cache_data
    def load_models():
        ollama_models = get_ollama_models()
        gemini_models = get_gemini_models()
        return ollama_models, gemini_models
    
    ollama_models, gemini_models = load_models()

    with st.sidebar:
        logo_path = "asset/LOGO.png"
        if os.path.exists(logo_path):
            st.image(logo_path, width=100)
        st.header(f"Bem-vindo, {st.session_state.get('user_name', 'Usuário')}!")
        if st.button("Logout"):
            if os.path.exists(plots_dir):
                shutil.rmtree(plots_dir)
            st.session_state.clear()
            if "GOOGLE_API_KEY" in os.environ:
                del os.environ["GOOGLE_API_KEY"]
            st.rerun()

        st.divider()
        st.header("⚙️ Configurações")
        llm_provider = st.selectbox("Escolha o Provedor de LLM:", ["Ollama", "Gemini"], index=1)
        selected_model = None
        if llm_provider == "Ollama":
            if ollama_models:
                selected_model = st.selectbox("Escolha o Modelo Ollama:", ollama_models)
            else:
                st.warning("Nenhum modelo Ollama encontrado.")
        elif llm_provider == "Gemini":
            if gemini_models:
                filtered_gemini_models = [m for m in gemini_models if 'gemini' in m]
                default_model = 'models/gemini-2.5-flash'
                default_index = filtered_gemini_models.index(default_model) if default_model in filtered_gemini_models else 0
                selected_model = st.selectbox("Escolha o Modelo Gemini:", filtered_gemini_models, index=default_index)
            else:
                st.warning("Nenhum modelo Gemini encontrado.")

        uploaded_file = st.file_uploader("Faça upload do seu arquivo CSV", type=["csv"])
        st.divider()
        st.header("Developer")
        show_thoughts = st.toggle("Mostrar pensamentos do agente", value=False)

        st.divider()
        st.header("📌 Relatório Gerado")
        
        if not st.session_state.pinned_items:
            st.info("Nenhum item foi adicionado ao relatório ainda.")
        else:
            for item in st.session_state.pinned_items:
                with st.expander(f"Interação de {item['timestamp']}"):
                    with st.chat_message("user"):
                        st.markdown(item['user_prompt'])
                    with st.chat_message("assistant"):
                        st.markdown(item['content'])
                        if item.get("image") and os.path.exists(item["image"]):
                            st.image(item["image"])

            if st.button("Limpar Itens Pinados", use_container_width=True):
                st.session_state.pinned_items = []
                st.toast("Itens pinados limpos!", icon="🧹")
                st.rerun()

            docx_data = generate_docx_report(st.session_state.pinned_items, st.session_state.get('user_name', 'Usuário'))
            st.download_button(
                label="Download Relatório (.docx)",
                data=docx_data,
                file_name=f"relatorio_jedi_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )

    if uploaded_file is not None:
        if st.session_state.get("current_file") != uploaded_file.name:
            if os.path.exists(plots_dir):
                shutil.rmtree(plots_dir)
            os.makedirs(plots_dir, exist_ok=True)
            st.session_state.messages = []
            st.session_state.current_file = uploaded_file.name
        try:
            df = pd.read_csv(uploaded_file)
            st.success("Arquivo CSV carregado com sucesso! As 5 primeiras linhas são:")
            st.dataframe(df.head())
            if "messages" not in st.session_state: st.session_state.messages = []

            for i, message in enumerate(st.session_state.messages):
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if message["role"] == "assistant":
                        if "image" in message and os.path.exists(message["image"]):
                            st.image(message["image"])
                        if "thoughts" in message and message["thoughts"]:
                            with st.expander("Ver pensamentos do Agente 🧠", expanded=True):
                                display_formatted_thoughts(message["thoughts"])
                        
                        item_id = f"message-{message['timestamp']}-{hash(message['content'])}"
                        is_pinned = any(item.get("id") == item_id for item in st.session_state.pinned_items)
                        pin_label = "📌 Pinado" if is_pinned else "🧷 Pinar"
                        if st.button(pin_label, key=f"pin_message_{i}"):
                            _pin_item(message)
                            st.rerun()

            if prompt := st.chat_input(f"{st.session_state.get('user_name', 'Usuário')}: Pergunte ao JEDI sobre os dados..."):
                st.session_state.messages.append({"role": "user", "content": prompt, "timestamp": datetime.datetime.now().isoformat()})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                llm = None
                if llm_provider == "Ollama":
                    if selected_model: llm = Ollama(model=selected_model, temperature=0)
                    else: st.error("Por favor, selecione um modelo Ollama disponível.")
                elif llm_provider == "Gemini":
                    if selected_model and os.getenv("GOOGLE_API_KEY"):
                        llm = ChatGoogleGenerativeAI(model=selected_model.replace('models/', ''), temperature=0)
                    else: st.error("Por favor, selecione um modelo Gemini.")
                
                if llm:
                    with st.spinner("O agente está pensando..."):
                        try:
                            agent = create_pandas_dataframe_agent(llm, df, agent_type="zero-shot-react-description", verbose=True, allow_dangerous_code=True, handle_parsing_errors=True)
                            plotting_instruction = f"IMPORTANTE: Se precisar criar um gráfico, use matplotlib e salve-o como 'plot.png'. Não use plt.show()."
                            history = "\n".join([f'{m['role']}: {m['content']}' for m in st.session_state.messages])
                            full_prompt = (
                                f"{plotting_instruction}\n\n"
                                    "Você é um agente de análise de dados amigável e prestativo. Sua principal tarefa é responder às perguntas do usuário sobre o DataFrame fornecido, usando as ferramentas disponíveis. "
                                    "Para perguntas relacionadas aos dados, seu raciocínio DEVE seguir o formato Thought, Action, Action Input, Observation, Final Answer. "
                                    "Se a pergunta do usuário não for sobre os dados (por exemplo, uma saudação), sua resposta DEVE seguir o formato 'Final Answer: [sua resposta conversacional]'. "
                                    "Se você não conseguir responder a uma pergunta sobre os dados, sua resposta final DEVE ser 'Final Answer: Não sei como responder a essa pergunta.'.\n\n"                                f"Baseado no histórico da conversa abaixo e no DataFrame, responda à pergunta do usuário:\n"
                                f"--- HISTÓRICO DA CONVERSA ---\n{history}\n"
                                f"--- PERGUNTA ATUAL ---\n{prompt}"
                            )
                            
                            response = ""
                            agent_thoughts_raw = ""
                            if show_thoughts:
                                string_io = io.StringIO()
                                with redirect_stdout(string_io):
                                    response = agent.run(full_prompt)
                                agent_thoughts_raw = string_io.getvalue()
                            else:
                                response = agent.run(full_prompt)
                            
                            assistant_message = {"role": "assistant", "content": response, "timestamp": datetime.datetime.now().isoformat()}
                            if agent_thoughts_raw:
                                assistant_message["thoughts"] = parse_agent_thoughts(agent_thoughts_raw)
                            
                            if os.path.exists("plot.png"):
                                if not os.path.exists(plots_dir): os.makedirs(plots_dir)
                                unique_filename = f"{uuid.uuid4()}.png"
                                new_path = os.path.join(plots_dir, unique_filename)
                                os.rename("plot.png", new_path)
                                assistant_message["image"] = new_path
                            
                            st.session_state.messages.append(assistant_message)
                            st.rerun()

                        except Exception as e:
                            st.error(f"Ocorreu um erro ao executar o agente: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro ao carregar o arquivo CSV: {e}")
    else:
        st.markdown("---")
        st.markdown("<h3 style='text-align: center;'>🚀 Comece sua Análise de Dados!</h3>", unsafe_allow_html=True)
        st.markdown("---")
        st.write("""
        Para iniciar, por favor, siga estes passos:
        1.  **Faça o Upload do seu CSV:** Use o botão "Faça upload do seu arquivo CSV" na barra lateral para carregar seus dados.
        2.  **Escolha seu LLM:** Selecione o provedor (Ollama ou Gemini) e o modelo na barra lateral.
        3.  **Faça Perguntas:** Após carregar o arquivo, use a caixa de chat abaixo para interagir com seus dados em linguagem natural.
        """)
        st.info("Dica: Ative o 'Mostrar pensamentos do agente' na barra lateral para entender como a IA está trabalhando!")