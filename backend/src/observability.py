import json
import logging
import os

import openlit
from dotenv import load_dotenv
from fastapi import FastAPI
from opentelemetry import trace
from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

load_dotenv()

logger = logging.getLogger(__name__)

tracer = trace.get_tracer("rag-backend")

RAG_TOKENS_TOTAL = Counter(
    "rag_tokens_total", "Total de tokens de LLM consumidos", ["type"]
)
RAG_RETRIEVAL_SECONDS = Histogram(
    "rag_retrieval_seconds", "Tempo gasto na busca por similaridade (embedding + consulta ao pgvector)"
)


class JsonFormatter(logging.Formatter):
    """Formata logs como JSON, correlacionados com trace_id/span_id do span atual."""

    def format(self, record: logging.LogRecord) -> str:
        span_context = trace.get_current_span().get_span_context()
        payload = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if span_context.is_valid:
            payload["trace_id"] = format(span_context.trace_id, "032x")
            payload["span_id"] = format(span_context.span_id, "016x")
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def log_event(event_logger: logging.Logger, level: int, message: str, **fields) -> None:
    """Loga uma mensagem incluindo trace_id/span_id do contexto atual, junto de campos extras."""
    span_context = trace.get_current_span().get_span_context()
    extra = dict(fields)
    if span_context.is_valid:
        extra["trace_id"] = format(span_context.trace_id, "032x")
        extra["span_id"] = format(span_context.span_id, "016x")
    event_logger.log(level, f"{message} | {extra}" if extra else message)


def setup_observability(app: FastAPI) -> None:
    """Configura logging estruturado, tracing (OpenTelemetry + openlit) e métricas (Prometheus)."""
    if not logging.getLogger().handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        logging.basicConfig(level=logging.INFO, handlers=[handler])

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318")
    service_name = os.getenv("OTEL_SERVICE_NAME", "rag-backend")

    try:
        openlit.init(
            otlp_endpoint=otlp_endpoint,
            application_name=service_name,
            environment=os.getenv("ENVIRONMENT", "production"),
        )
    except Exception:
        logger.warning("Falha ao inicializar openlit/OTLP em %s; seguindo sem tracing de LLM.", otlp_endpoint)

    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
