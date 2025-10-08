from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_experimental.agents import create_pandas_dataframe_agent
import pandas as pd
import io
from contextlib import redirect_stdout
import re

def run_guardian_query(llm: ChatGoogleGenerativeAI, df: pd.DataFrame, query: str, record_thoughts: bool = False) -> dict:
    """
    Executa uma consulta em um DataFrame pandas e retorna um dicionário com o resultado e os pensamentos.
    """
    prompt_template = f"""
    Você é um agente de análise de dados focado em execução. Seu único propósito é executar código Python em um DataFrame pandas para responder a uma pergunta.
    - Você não deve fornecer nenhum texto de conversação ou explicações.
    - Sua resposta final deve ser a saída bruta do código Python.
    - A pergunta do usuário é: '{query}'
    - Responda no mesmo idioma da pergunta do usuário.
    """

    guardian_agent = create_pandas_dataframe_agent(
        llm, df, agent_type="zero-shot-react-description",
        verbose=record_thoughts, allow_dangerous_code=True
    )

    try:
        agent_log = ""
        result = ""
        if record_thoughts:
            string_io = io.StringIO()
            with redirect_stdout(string_io):
                response = guardian_agent.invoke({"input": prompt_template})
                result = response['output']
            agent_log = string_io.getvalue()
        else:
            response = guardian_agent.invoke({"input": prompt_template})
            result = response['output']

        final_result = result
        if agent_log and '> Finished chain.' in agent_log:
            observations = re.findall(r"Observation: (.*?)(?:Thought:|$)", agent_log, re.DOTALL)
            if observations:
                final_result = observations[-1].strip()

        return {"result": final_result, "thoughts": agent_log}

    except Exception as e:
        return {"result": f"Guardian agent failed: {str(e)}", "thoughts": agent_log if 'agent_log' in locals() else str(e)}
