import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent.agent import ask, ask_stream
from agent.tools import get_ultimos_resultados
from ingestion.run_ingestion import run_injestion
from ingestion.setup_db import create_table, get_connection

load_dotenv()

logger = logging.getLogger(__name__)


def parse_allowed_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


ALLOWED_ORIGINS = parse_allowed_origins(os.getenv("ALLOWED_ORIGINS", ""))


def seed_database_if_empty() -> None:
    """Cria a tabela (se preciso) e popula com o dataset embutido na imagem
    caso o banco ainda esteja vazio. Idempotente: insert usa ON CONFLICT DO
    NOTHING e so roda a ingestao de fato quando a tabela nao tem linhas.
    """
    try:
        create_table()

        conn = get_connection()
        try:
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM conversation;")
            total = cur.fetchone()[0]
        finally:
            conn.close()

        if total == 0:
            logger.info("Tabela 'conversation' vazia, iniciando ingestao automatica...")
            run_injestion()
        else:
            logger.info("Tabela 'conversation' ja possui %s linhas, pulando ingestao.", total)
    except Exception:
        logger.exception("Falha ao popular o banco automaticamente no startup.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(asyncio.to_thread(seed_database_if_empty))
    yield


app = FastAPI(title="RAG Customer Service API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health() -> dict[str, str]:
    return {"status": "ok"}


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    content: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer = ask(request.message)
        fontes = get_ultimos_resultados()
        sources = [
            Source(content=fonte["content"], similarity=fonte["similarity"])
            for fonte in fontes
        ]
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        print(f"[ERRO] Falha no endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a pergunta.")


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def event_generator():
        async for event in ask_stream(request.message):
            yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Accel-Buffering": "no",
        },
    )
