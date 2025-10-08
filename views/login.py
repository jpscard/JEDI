# --- Importações Essenciais ---
import streamlit as st
import os
import base64
from utils import validate_gemini_api_key

def login_page():
    st.set_page_config(page_title="Login - JEDI", layout="centered")
    """Exibe a página de login em um layout centralizado."""
    _, col, _ = st.columns([1, 2, 1])
    with col:
        logo_path = "asset/LOGO.png"
        if os.path.exists(logo_path):
            with open(logo_path, "rb") as f:
                data = base64.b64encode(f.read()).decode("utf-8")
            st.markdown(f"<div style='text-align: center'><img src='data:image/png;base64,{data}' width='200'></div>", unsafe_allow_html=True)
                
        name = st.text_input("Seu Nome", key="login_name")
        password = st.text_input("Insira sua API Key do Gemini", type="password", key="login_password")
        
        if st.button("Login", use_container_width=True, type="primary"):
            if name and password:
                if validate_gemini_api_key(password):
                    st.session_state["logged_in"] = True
                    st.session_state["user_name"] = name
                    os.environ["GOOGLE_API_KEY"] = password
                    st.success("Login bem-sucedido!")
                    st.rerun()
            else:
                st.error("Por favor, insira seu nome e a API Key.")