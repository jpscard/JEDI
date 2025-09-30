# --- Importações Essenciais ---
import streamlit as st
import re
import ollama
import google.generativeai as genai
from google.api_core import exceptions

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

def display_formatted_thoughts(parsed_thoughts):
    """Exibe os pensamentos do agente de forma formatada no Streamlit."""
    for i, step in enumerate(parsed_thoughts):
        if step["type"] == "Thought":
            st.markdown(f"🤔 **Pensamento**")
            st.markdown(f"> {step['content'].strip()}")
        elif step["type"] == "Action":
            st.markdown(f"🎬 **Ação:** `{step['content']}`")
        elif step["type"] == "Action Input":
            st.markdown(f"⌨️ **Input da Ação**")
            st.code(step['content'], language='python')
        elif step["type"] == "Observation":
            st.markdown(f"🔍 **Observação**")
            st.text(step['content'])
        if i < len(parsed_thoughts) - 1:
            st.markdown("--- ")

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
        st.warning(f"Ollama não parece estar rodando. Erro: {e}")
        return []

def get_gemini_models():
    try:
        return [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    except Exception as e:
        st.warning(f"Não foi possível buscar modelos Gemini. Verifique a API Key. Erro: {e}")
        return []
