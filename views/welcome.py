# --- Importações Essenciais ---
import streamlit as st
import base64
import os

def welcome_screen():
    st.set_page_config(page_title="Bem-vindo ao JEDI", layout="centered")
    """Exibe a tela de boas-vindas e instruções."""
    
    # Adiciona a logo centralizada
    logo_path = "asset/LOGO.png"
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        st.markdown(f"<div style='text-align: center'><img src='data:image/png;base64,{data}' width='200'></div>", unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center;'>Bem-vindo ao JEDI: João's Exploratory Data Insight!</h1>", unsafe_allow_html=True)

    st.markdown(" ") # Espaçamento

    # Centraliza o botão
    _ , btn_col, _ = st.columns([2.5, 1, 2.5])
    with btn_col:
        if st.button("Entrar", use_container_width=True, type="primary"):
            st.session_state.welcome_seen = True
            st.rerun()
    st.markdown(" ") # Espaçamento

    with st.expander("🎯 Sobre o Projeto (Clique para expandir)"):
        st.write("""
        Bem-vindo ao **JEDI: João's Exploratory Data Insight**! 🚀
        Aqui, você se tornará um verdadeiro Mestre Jedi na arte da análise de dados. Este sistema utiliza o poder da Inteligência Artificial e de agentes autônomos para desvendar os segredos escondidos em seus arquivos CSV.
        Com o JEDI, você pode 'conversar' com seus dados em linguagem natural, obtendo insights profundos, resumos detalhados e visualizações gráficas impressionantes. Prepare-se para dominar a Força dos Dados!
        """)

    st.markdown(" ") # Espaçamento

    with st.expander("📖 Como Usar (Clique para expandir)"):
        st.markdown("""
        1.  **Faça o Login:** Na próxima tela, você precisará de uma API Key válida do Google Gemini para se autenticar.
        2.  **Carregue seus Dados:** Na barra lateral, clique em "Faça upload do seu arquivo CSV" e selecione o arquivo que deseja analisar.
        3.  **Configure o Agente:** Escolha qual provedor de LLM (Ollama para modelos locais ou Gemini para modelos Google) e qual modelo específico você quer usar.
        4.  **Converse com seus Dados:** Use a caixa de chat na parte inferior da tela para fazer suas perguntas. Por exemplo:
            - *"Quais são as colunas mais importantes?"*
            - *"Mostre um resumo estatístico dos dados."*
            - *"Crie um gráfico de barras da coluna X."*
            - *"Existe alguma correlação entre as colunas Y e Z?"*
        5.  **Modo Desenvolvedor (Opcional):** Ative a opção "Mostrar pensamentos do agente" na barra lateral para ver o passo a passo de como a IA está raciocinando.
        6.  **Crie e Baixe Relatórios:** Ao lado de cada resposta do agente, você encontrará um botão para "pinar" (🧷) a resposta. Itens pinados aparecerão no relatório na barra lateral. Você pode visualizar, limpar e fazer o download do relatório em formato `.docx` a qualquer momento.
        """)
  
    # Nova seção para o README.md
    st.markdown(" ") # Espaçamento
    with st.expander("📚 Documentação Completa (README)"):
        readme_path = "README.md"
        if os.path.exists(readme_path):
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read()
            
            # Skip the main title of the README
            readme_lines = readme_content.split('\n')
            display_content = '\n'.join(readme_lines[1:])

            st.markdown(display_content, unsafe_allow_html=True)
        else:
            st.warning("README.md não encontrado. Por favor, crie o arquivo para ver as instruções.")
    
    # Seção de Identificação do Desenvolvedor
    st.markdown("<h3 style='text-align: center;'>Desenvolvido por</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>João Paulo Cardoso</p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>LinkedIn: <a href='https://www.linkedin.com/in/joao-paulo-cardoso/' target='_blank'>linkedin.com/in/joao-paulo-cardoso/</a></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align: center;'>GitHub do Projeto: <a href='https://github.com/jpscard/JEDI' target='_blank'>github.com/jpscard/JEDI</a></p>", unsafe_allow_html=True)
    
