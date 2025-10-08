from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import pandas as pd
import os
import uuid
import io
from contextlib import redirect_stdout
import matplotlib
matplotlib.use('Agg')
import seaborn as sns
import matplotlib.pyplot as plt

def create_static_plot(llm: ChatGoogleGenerativeAI, df: pd.DataFrame, plot_instruction: str, record_thoughts: bool = False) -> dict:
    """
    Usa um agente dedicado para gerar um gráfico estático de alta qualidade com Seaborn,
    salva-o como um arquivo PNG e retorna um dicionário com o caminho e os pensamentos.
    """
    unique_filename = f"{uuid.uuid4()}.png"
    png_path = f"temp_plots/{unique_filename}"

    sns.set_theme(style="whitegrid")

    prompt = f"""
    Você é um especialista em visualização de dados, criando gráficos de alta qualidade com Seaborn.
    Sua tarefa é criar uma única visualização com base na solicitação do usuário.

    Solicitação do usuário: '{plot_instruction}'

    Você DEVE usar a biblioteca 'seaborn' (importada como `sns`) e 'matplotlib.pyplot' (importada como `plt`) para gerar o gráfico.
    Após criar o gráfico, você DEVE salvá-lo no seguinte caminho: '{png_path}'
    Use `plt.savefig('{png_path}')`. Limpe a figura após salvar com `plt.close()`.
    Não use `plt.show()`.

    Sua resposta final DEVE ser o caminho para o arquivo PNG salvo: '{png_path}'
    """
    
    static_agent = create_pandas_dataframe_agent(
        llm, df, agent_type="zero-shot-react-description",
        verbose=record_thoughts, allow_dangerous_code=True
    )

    try:
        agent_log = ""
        result_path = ""
        if record_thoughts:
            string_io = io.StringIO()
            with redirect_stdout(string_io):
                response = static_agent.invoke({"input": prompt})
                result_path = response['output']
            agent_log = string_io.getvalue()
        else:
            response = static_agent.invoke({"input": prompt})
            result_path = response['output']
        
        final_path = ""
        if os.path.exists(png_path):
            final_path = png_path
        elif isinstance(result_path, str) and os.path.exists(result_path.strip()):
            final_path = result_path.strip()
        else:
            final_path = "Artesão Estático criou um gráfico, mas não consegui encontrar o caminho do arquivo."
        
        return {"result": final_path, "thoughts": agent_log}

    except Exception as e:
        return {"result": f"A forja do Artesão Estático esfriou. A plotagem falhou: {str(e)}", "thoughts": agent_log if 'agent_log' in locals() else str(e)}