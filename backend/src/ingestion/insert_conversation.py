import psycopg2
from pgvector.psycopg2 import register_vector
from ingestion.setup_db import get_connection

def insert_conversation(
     conversation_id: str,
    content: str,
    embedding: list[float],
    intent: str,
    sector: str,
    sentiment: str,
) -> bool:
    """Insere uma conversa processada na tabela conversations.
    Retorna True se inseriu com sucesso, False se falhou.
    """
    conn = get_connection()

    try:
        register_vector(conn) # ensina o psycopg2 a entender o tipo VECTOR
        cur = conn.cursor()
        cur.execute(
           """
            INSERT INTO conversation
                (conversation_id, content, embedding, intent, sector, sentiment)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (conversation_id) DO NOTHING;
            """,
           (conversation_id, content, embedding, intent, sector, sentiment),
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.rollback()
        print(f"Erro ao inserir conversa {conversation_id}: {e}")
        return False
    finally:
        conn.close()
