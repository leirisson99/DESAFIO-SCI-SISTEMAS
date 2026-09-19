from fastapi import FastAPI
from pydantic import BaseModel

from agent.agent import ask
from retrival.search import search_similarit_conversation

app = FastAPI(title="RAG Customer Service API")


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
    answer = ask(request.message)
    sources = search_similarit_conversation(request.message)
    return ChatResponse(answer=answer, sources=sources)
