# --- Importações Essenciais ---
import streamlit as st

# Importa as funções de cada página
from views.welcome import welcome_screen
from views.login import login_page
from views.main_app import main_app

# --- CONFIGURAÇÃO DA PÁGINA (DEVE SER O PRIMEIRO COMANDO STREAMLIT) ---
st.set_page_config(
    page_title="Agente EDA com LangChain",
    layout="wide",
    initial_sidebar_state="auto"
)

# --- Bloco de Execução Principal (Roteador) ---

# Inicializa o estado da sessão se não existir
if "welcome_seen" not in st.session_state:
    st.session_state.welcome_seen = False
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "pinned_items" not in st.session_state:
    st.session_state.pinned_items = []
if "show_report" not in st.session_state:
    st.session_state.show_report = False

# Controla qual página é exibida
if not st.session_state.welcome_seen:
    welcome_screen()
elif not st.session_state.logged_in:
    login_page()
else:
    main_app()