# ✨ JEDI: João's Exploratory Data Insight

## 🚀 Visão Geral do Projeto

Bem-vindo ao **JEDI: João's Exploratory Data Insight**! Este sistema inovador transforma a maneira como você interage com seus dados. Utilizando o poder dos Grandes Modelos de Linguagem (LLMs) e agentes inteligentes, o JEDI permite que você realize Análise Exploratória de Dados (EDA) em arquivos CSV através de uma interface de chat intuitiva.

Com o JEDI, você pode:
*   **Conversar com seus Dados:** Faça perguntas em linguagem natural e obtenha respostas, insights e resumos.
*   **Visualizações Gráficas:** Solicite a criação de gráficos para visualizar tendências e padrões.
*   **Escolha de LLM:** Selecione entre modelos locais (Ollama) ou da nuvem (Google Gemini) para suas análises.
*   **Transparência do Agente:** Ative o "Modo Desenvolvedor" para acompanhar o raciocínio passo a passo do agente de IA.

Prepare-se para dominar a Força dos Dados e desvendar os segredos escondidos em suas informações!

## 🌟 Funcionalidades Principais

*   **Autenticação Segura:** Login com validação de API Key do Google Gemini.
*   **Interface Intuitiva:** Tela de boas-vindas com instruções claras e design aprimorado.
*   **Upload de CSV:** Carregue facilmente seus arquivos de dados para análise.
*   **Seleção de Modelos:** Escolha dinamicamente entre modelos Ollama (locais) e Gemini (Google).
*   **Agente de EDA:** Um agente inteligente baseado em LangChain para interagir com DataFrames.
*   **Geração de Gráficos:** Capacidade de gerar e exibir gráficos matplotlib.
*   **Modo Desenvolvedor:** Visualize o "pensamento" detalhado do agente para depuração e aprendizado.
*   **Relatórios Dinâmicos:** Pine as respostas do agente no chat para criar um relatório dinâmico na barra lateral, com opção de download em formato `.docx`.
*   **Tema Personalizável:** Configuração de tema via `.streamlit/config.toml`.

## 📂 Estrutura do Projeto

O projeto JEDI é modularizado para facilitar a manutenção e expansão:

```
.
├── .streamlit/             # Configurações do Streamlit (ex: tema)
│   └── config.toml
├── asset/                  # Ativos do projeto (ex: LOGO.png)
│   └── LOGO.png
├── views/                  # Módulos da interface do usuário (páginas)
│   ├── __init__.py
│   ├── login.py            # Tela de login
│   ├── main_app.py         # Aplicação principal de chat e EDA
│   └── welcome.py          # Tela de boas-vindas e instruções
├── utils.py                # Funções utilitárias e helpers (validação, parsers, etc.)
├── app.py                  # Ponto de entrada principal e roteador de páginas
├── requirements.txt        # Dependências do projeto
└── README.md               # Este arquivo
```

## 🛠️ Como Usar

### Pré-requisitos

*   **Python 3.9+**
*   **Ollama (Opcional):** Para usar modelos locais, instale o Ollama e baixe um modelo (ex: `ollama pull llama3`).
*   **Google Gemini API Key:** Necessária para autenticação e uso dos modelos Gemini. Obtenha a sua em [Google AI Studio](https://aistudio.google.com/app/apikey).

### Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/jpscard/JEDI.git
    cd JEDI
    ```

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv .venv
    # No Windows
    .venv\Scripts\activate
    # No macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

### Executando o Aplicativo

1.  **Inicie o Ollama (se for usar modelos locais):**
    ```bash
    ollama run llama3 # ou o modelo de sua preferência
    ```

2.  **Execute o aplicativo Streamlit:**
    ```bash
    streamlit run app.py
    ```

3.  Abra o navegador na URL fornecida pelo Streamlit (geralmente `http://localhost:8501`).

### Uso Básico

1.  **Tela de Boas-Vindas:** Leia as instruções e clique em "Prosseguir para o Login".
2.  **Login:** Insira seu nome e sua API Key do Google Gemini.
3.  **Aplicação Principal:**
    *   Faça o upload de um arquivo CSV na barra lateral.
    *   Selecione o provedor de LLM (Ollama ou Gemini) e o modelo.
    *   Comece a fazer perguntas sobre seus dados na caixa de chat!
    *   **Crie Relatórios:** Clique no ícone de "Pinar" (🧷) em qualquer resposta do agente para adicioná-la a um relatório na barra lateral. Você pode visualizar, limpar e fazer o download do relatório em formato `.docx` diretamente pela barra lateral.

## 🎨 Personalização

*   **Tema:** Edite o arquivo `.streamlit/config.toml` para ajustar cores, fontes e outros aspectos visuais.
*   **Logo:** Substitua o arquivo `asset/LOGO.png` pela sua própria imagem.

## 👨‍💻 Desenvolvedor

**João Paulo Cardoso**
*   **LinkedIn:** [https://www.linkedin.com/in/joao-paulo-cardoso/](https://www.linkedin.com/in/joao-paulo-cardoso/)
*   **GitHub do Projeto:** [https://github.com/jpscard/JEDI](https://github.com/jpscard/JEDI)

---
*Gerado com a ajuda de um assistente de IA.*
