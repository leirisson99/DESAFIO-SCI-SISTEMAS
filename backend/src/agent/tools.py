from strands import tool
from retrival.search import search_similarit_conversation
from contextvars import ContextVar
from strands import Agent


# Cada requisição/contexto de execução tem sua própria cópia isolada dessa variável
ultimos_resultados_var: ContextVar[list] = ContextVar("ultimos_resultados", default=[])


@tool
def seek_knowledge(question: str, agent: Agent | None = None) -> str:
    """Busca conversas de atendimento ao cliente relevantes para responder à pergunta do usuário.
    Use esta ferramenta sempre que precisar de informação para responder qualquer pergunta
    sobre atendimento, pedidos, cancelamentos, promoções ou outros temas de e-commerce.
    """
    results = search_similarit_conversation(question)

    # agent.state tem lock interno e é a mesma instância que ask() criou —
    # funciona independente de em que thread/task a strands rodar a tool.
    if agent is not None:
        agent.state.set("ultimos_resultados", results)

    if not results:
        return "Nenhuma informação relevante foi encontrada na base de conhecimento para essa pergunta."

    partes = []
    for result in results:
        partes.append(
            f"[Conversa {result['conversation_id']} | setor: {result['sector']} | similaridade: {result['similarity']:.2f}]\n"
f"{result['content']}"
        )
    return "\n\n---\n\n".join(partes)


def get_ultimos_resultados() -> list:
    """Recupera os resultados da última busca feita no contexto atual (usado pela API para montar as fontes)."""
    return ultimos_resultados_var.get()