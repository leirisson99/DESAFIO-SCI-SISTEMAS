import logging
import os
from typing import AsyncIterator

from dotenv import load_dotenv
from strands import Agent
from strands.models.openai import OpenAIModel

from agent.tools import seek_knowledge, ultimos_resultados_var
from agent.prompts import SYSTEM_PROMPT
from observability import RAG_TOKENS_TOTAL, tracer

load_dotenv()

logger = logging.getLogger(__name__)


model = OpenAIModel(
    client_args = {"api_key" : os.getenv("OPENAI_API_KEY")},
    model_id= os.getenv("MODEL", "gpt-4o-mini")
)




def _record_usage(span, get_usage) -> None:
    """Registra atributos gen_ai.usage.* no span e incrementa os contadores Prometheus.
    Nunca deve derrubar o fluxo principal — falhas aqui são só de telemetria.
    """
    try:
        usage = get_usage()
        input_tokens = usage.get("inputTokens", 0)
        output_tokens = usage.get("outputTokens", 0)
        total_tokens = usage.get("totalTokens", 0)
        span.set_attribute("gen_ai.usage.input_tokens", input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", output_tokens)
        span.set_attribute("gen_ai.usage.total_tokens", total_tokens)
        RAG_TOKENS_TOTAL.labels(type="input").inc(input_tokens)
        RAG_TOKENS_TOTAL.labels(type="output").inc(output_tokens)
        RAG_TOKENS_TOTAL.labels(type="total").inc(total_tokens)
    except Exception:
        logger.warning("Não foi possível registrar métricas de uso de tokens.", exc_info=True)


def ask(question: str) -> str:
    """Envia uma pergunta ao agente e devolve a resposta como texto.
    Em caso de falha (API, rede, etc.), devolve uma mensagem amigável ao usuário
    e registra o erro real para depuração.
    """
    if not question or not question.strip():
         ultimos_resultados_var.set([])
         return "Por favor, envie uma pergunta para que eu possa ajudar."

    with tracer.start_as_current_span("rag.pipeline") as span:
        span.set_attribute("gen_ai.request.model", os.getenv("MODEL", "gpt-4o-mini"))
        try:
            agent = Agent(
                model=model,
                system_prompt=SYSTEM_PROMPT,
                tools=[seek_knowledge],
            )
            response = agent(question)
            ultimos_resultados_var.set(agent.state.get("ultimos_resultados") or [])
            _record_usage(span, lambda: response.metrics.accumulated_usage)
            return str(response)
        except Exception as e:
            ultimos_resultados_var.set([])
            span.record_exception(e)
            logger.exception("Falha ao processar pergunta '%s'", question)
            return "Desculpe, ocorreu um problema ao processar sua pergunta. Tente novamente em instantes."


async def ask_stream(question: str) -> AsyncIterator[dict]:
    """Envia uma pergunta ao agente e produz eventos de streaming conforme a
    resposta é gerada.

    Cada evento produzido é um dict com um campo "type":
    - {"type": "delta", "text": str}: um pedaço de texto da resposta.
    - {"type": "done", "sources": list}: fim do stream, com as fontes usadas.
    - {"type": "error", "message": str}: falha ao processar a pergunta.
    """
    if not question or not question.strip():
        ultimos_resultados_var.set([])
        yield {
            "type": "delta",
            "text": "Por favor, envie uma pergunta para que eu possa ajudar.",
        }
        yield {"type": "done", "sources": []}
        return

    with tracer.start_as_current_span("rag.pipeline") as span:
        span.set_attribute("gen_ai.request.model", os.getenv("MODEL", "gpt-4o-mini"))
        try:
            agent = Agent(
                model=model,
                system_prompt=SYSTEM_PROMPT,
                tools=[seek_knowledge],
            )
            async for event in agent.stream_async(question):
                if "data" in event:
                    yield {"type": "delta", "text": event["data"]}

            resultados = agent.state.get("ultimos_resultados") or []
            ultimos_resultados_var.set(resultados)
            _record_usage(span, lambda: agent.event_loop_metrics.accumulated_usage)
            sources = [
                {"content": resultado["content"], "similarity": resultado["similarity"]}
                for resultado in resultados
            ]
            yield {"type": "done", "sources": sources}
        except Exception as e:
            ultimos_resultados_var.set([])
            span.record_exception(e)
            logger.exception("Falha ao processar pergunta '%s'", question)
            yield {
                "type": "error",
                "message": "Desculpe, ocorreu um problema ao processar sua pergunta. Tente novamente em instantes.",
            }


