import os
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()

api_key=os.getenv("OPENAI_API_KEY")
embedding_model = os.getenv("EMBEDDING_MODEL")

client = OpenAI(api_key=api_key)

def generation_embedding(text: str) -> list[float] | None:
    """Gera o vetor de embedding para um texto usando a API da OpenAI.
    Retorna None se o texto for vazio ou se a chamada falhar.
    """

    if not text or not text.strip():
        print("AVISO: o texto está vazio, embedding não gerado.")
        return None

    try:

        response = client.embeddings.create(
            model=embedding_model,
            input=text
        )

        return response.data[0].embedding
    except Exception as e:
        print(f"Erro ao gerar embedding: {e}")
        return None


    