from strands import tool
from retrival.search import search_similarit_conversation

@tool
def seek_knowledge(question: str) -> str:
    """
    Busca conversas de atendimento ao cliente relevantes para responder à pergunta do usuário.
    Use esta ferramenta sempre que precisar de informação para responder qualquer pergunta
    sobre atendimento, pedidos, cancelamentos, promoções ou outros temas de e-commerce.
    """
    results = search_similarit_conversation(question)

    if not results:
        return "Nenhuma informação relevante foi encontrada na base de conhecimento para essa pergunta."

    partes = []
    for result in results:
        partes.append(
            f"[Conversa {result['conversation_id']} | setor: {result['sector']} | similaridade: {result['similarity']:.2f}]\n"
f"{result['content']}"
        )
    return "\n\n---\n\n".join(partes)


if __name__ == "__main__":
    resultado = seek_knowledge("meu pedido não chegou, o que faço?")
    print(resultado)

    resultado_vazio = seek_knowledge("qual a capital da França?")
    print(resultado_vazio)