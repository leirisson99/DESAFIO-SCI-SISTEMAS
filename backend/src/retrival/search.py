from pgvector.psycopg2 import register_vector
from ingestion.setup_db import get_connection
from ingestion.embed_and_store import generation_embedding
from dotenv import load_dotenv
import os

load_dotenv()

def search_similarit_conversation(query: str, k: int = int(os.getenv("TOP_K", 3))) -> list[dict]:
    """Busca as k conversas mais similares semanticamente à pergunta do usuário.
    Retorna lista de dicionários com content, metadados e score de similaridade.
    """
    query_embedding = generation_embedding(query)
    if query_embedding is None:
        print("Não foi possível gerar embedding para a pergunta.")
        return []

    conn = get_connection()
    try:
        register_vector(conn)
        cur = conn.cursor()
        cur.execute(
            """
SELECT 
conversation_id,
content,
intent,
sector,
sentiment,
1 - (embedding <=> %s) AS similarity
FROM conversation
ORDER BY embedding <=> %s
LIMIT %s
""",
(query_embedding, query_embedding, k)
        )
        result = cur.fetchall()
        cur.close()
    except Exception as e:
        print(f"Erro na busca por similaridade: {e}")
        return []
    finally:
        conn.close()
    return [
        { "conversation_id": row[0],
                "content": row[1],
                "intent": row[2],
                "sector" : row[3],
                "sentiment" : row[4],
                "similarity" : row[5]
                }
                for row in result
    ]
  
    