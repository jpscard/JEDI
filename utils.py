# --- Importações Essenciais ---
import streamlit as st
import pandas as pd
import re
import ollama
import google.generativeai as genai
from google.api_core import exceptions

# --- Funções de Profiling de Dados ---
def get_data_profile(df):
    """
    Gera um perfil detalhado de um DataFrame para ser usado no prompt do agente.
    """
    profile = []
    profile.append(f"O DataFrame tem {df.shape[0]} linhas e {df.shape[1]} colunas.")
    
    profile.append("\n### Resumo das Colunas:")
    for col in df.columns:
        dtype = str(df[col].dtype)
        missing_values = df[col].isnull().sum()
        missing_percentage = (missing_values / df.shape[0]) * 100
        
        col_summary = [f"- **Coluna '{col}'**:"]
        col_summary.append(f"  - Tipo de Dado: `{dtype}`")
        col_summary.append(f"  - Valores Ausentes: {missing_values} ({missing_percentage:.2f}%)")
        
        if pd.api.types.is_numeric_dtype(df[col]):
            desc = df[col].describe()
            col_summary.append(f"  - Média: {desc['mean']:.2f}")
            col_summary.append(f"  - Desvio Padrão: {desc['std']:.2f}")
            col_summary.append(f"  - Mínimo: {desc['min']:.2f}")
            col_summary.append(f"  - Máximo: {desc['max']:.2f}")
        else:
            unique_values = df[col].nunique()
            col_summary.append(f"  - Valores Únicos: {unique_values}")
            if unique_values < 15: # Mostra os valores se forem poucos
                top_values = df[col].value_counts().head(5)
                col_summary.append("  - Valores Comuns:")
                for val, count in top_values.items():
                    col_summary.append(f"    - '{val}': {count} vezes")

        profile.append("\n".join(col_summary))
        
    return "\n".join(profile)

# --- Funções de Formatação de Pensamentos do Agente ---
def parse_agent_thoughts(thought_string):
    """Analisa a string de saída do agente e a transforma em uma lista estruturada."""
    ansi_escape = re.compile(r'\x1B(?:[@\-Z\\\-_]|(?:\[[0-?]*[ -/]*[@-~]))')
    thought_string = ansi_escape.sub('', thought_string)
    if '> Finished chain.' in thought_string:
        thought_string = thought_string.split('> Finished chain.')[0]
    pattern = re.compile(r"(Thought|Action|Action Input|Observation):(.+?)(?=(Thought|Action|Action Input|Observation):|> Entering new AgentExecutor chain.|$)", re.DOTALL)
    matches = pattern.findall(thought_string)
    parsed_steps = []
    for match in matches:
        step_type = match[0].strip()
        content = match[1].strip()
        parsed_steps.append({"type": step_type, "content": content})
    return parsed_steps

def display_formatted_thoughts(log_entries: list):
    """Exibe um log de pensamentos/eventos de forma formatada."""
    for entry in log_entries:
        st.markdown(entry)
        st.markdown("---")

# --- Funções de Validação e Obtenção de Modelos ---
def validate_gemini_api_key(api_key):
    try:
        genai.configure(api_key=api_key)
        genai.list_models()
        return True
    except exceptions.PermissionDenied:
        st.error("Chave de API do Gemini inválida ou sem permissão.")
        return False
    except Exception as e:
        st.error(f"Ocorreu um erro ao validar a chave de API: {e}")
        return False

def get_ollama_models():
    try:
        response = ollama.list()
        return [model['model'] for model in response['models']]
    except Exception as e:
        # Ollama não está disponível, retorna uma lista vazia silenciosamente.
        # O erro é impresso no console para depuração local.
        print(f"Ollama check failed: {e}")
        return []

def get_gemini_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        st.warning(f"Não foi possível buscar modelos Gemini. Verifique a API Key. Erro: {e}")
        return []
