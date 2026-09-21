from pgvector.psycopg2 import register_vector
from ingestion.setup_db import get_connection
from ingestion.embed_and_store import generation_embedding
from dotenv import load_dotenv
from pgvector import Vector
import logging
import os

from observability import tracer

load_dotenv()

logger = logging.getLogger(__name__)

SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.40))
TOP_K =  int(os.getenv("TOP_K", 3))

def search_similarit_conversation(query: str, k: int = TOP_K) -> list[dict]:
    """Busca as k conversas mais similares semanticamente à pergunta do usuário.
    Retorna lista de dicionários com content, metadados e score de similaridade.
    """

    with tracer.start_as_current_span("rag.embedding"):
        query_embedding = generation_embedding(query)
    if query_embedding is None:
        logger.warning("Não foi possível gerar embedding para a pergunta.")
        return []

    conn = get_connection()
    try:
        register_vector(conn)
        cur = conn.cursor()
        with tracer.start_as_current_span("rag.db_query"):
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
(Vector(query_embedding), Vector(query_embedding), k),
            )
            result = cur.fetchall()
        cur.close()
    except Exception:
        logger.exception("Erro na busca por similaridade")
        return []
    finally:
        conn.close()
    resultado_filtrado = [
        { "conversation_id": row[0],
                "content": row[1],
                "intent": row[2],
                "sector" : row[3],
                "sentiment" : row[4],
                "similarity" : row[5]
                }
                for row in result
                if row[5] >= SIMILARITY_THRESHOLD
    ]

    return resultado_filtrado
  
