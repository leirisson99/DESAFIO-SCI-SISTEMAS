import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agent.agent import ask
from agent.tools import get_ultimos_resultados

load_dotenv()


def parse_allowed_origins(value: str) -> list[str]:
    return [origin.strip() for origin in value.split(",") if origin.strip()]


ALLOWED_ORIGINS = parse_allowed_origins(os.getenv("ALLOWED_ORIGINS", ""))

app = FastAPI(title="RAG Customer Service API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class Source(BaseModel):
    conversation_id: str
    content: str
    intent: str
    sector: str
    sentiment: str
    similarity: float


class ChatResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer = ask(request.message)
        fontes = get_ultimos_resultados()
        return ChatResponse(answer=answer, sources=fontes)
    except Exception as e:
        print(f"[ERRO] Falha no endpoint /chat: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao processar a pergunta.")
