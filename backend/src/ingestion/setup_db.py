import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("DATABASE_URL não encontrada no .env")
    return psycopg2.connect(database_url)


def create_table():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        cur.execute("""
CREATE TABLE IF NOT EXISTS conversation (
id SERIAL PRIMARY KEY,
conversation_id TEXT NOT NULL UNIQUE,
content TEXT NOT NULL,
embedding VECTOR(1536) NOT NULL,
intent TEXT,
sector TEXT,
sentiment TEXT
);
""")
        conn.commit()
        cur.close()
        print("Tabela 'conversation criada com sucesso' ou já existe")

    except Exception as e:
        conn.rollback()
        print(f"Error ao criar tabela: {e}")
    finally:
        cur.close()

if __name__ == "__main__":
    create_table()