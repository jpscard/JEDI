from langchain_google_genai import ChatGoogleGenerativeAI

def get_sage_interpretation(llm: ChatGoogleGenerativeAI, data_context: str, user_query: str) -> str:
    """
    Uses an LLM to interpret raw data or analysis results in a conversational,
    thematic way, acting as the \'Sage\' of the Jedi Council.
    """
    prompt = f"""
Você é um Sábio Jedi. Seu papel é interpretar dados complexos para os outros,
encontrando a história e o significado dentro dos números. Você fala de uma maneira clara, perspicaz,
e levemente temática.

Um Guardião de Dados forneceu a seguinte análise de dados brutos com base na consulta do usuário:
---
Consulta Original do Usuário: "{user_query}"
---
Dados Brutos/Análise:
{data_context}
---

Sua tarefa é explicar o que esses dados significam para o usuário.
Concentre-se nas percepções mais importantes e responda à consulta original do usuário.
Não apenas repita os números; explique seu significado.
Comece sua resposta com uma abertura sábia e temática.
Responda sempre no mesmo idioma da \'Consulta Original do Usuário\'.
"""

    try:
        response = llm.invoke(prompt)
        # The response from invoke is an AIMessage object, we need its content
        return response.content.strip()
    except Exception as e:
        return f"The Sage is having trouble interpreting the Force. Error: {str(e)}"
