


def format_conversation(messages: list[dict]) -> str:
    if not messages:
        return ""

    lines = []
    for turn in messages:
        role = turn.get("role", "desconhecido").strip()
        content = turn.get("content", "").strip()
        if content:
            lines.append(f"{role} : {content}")
    return "\n".join(lines)


def preparation_conversation(conversation: dict) -> dict:
    """Prepara uma conversa separando texto (pro embedding) de metadados."""
    return {
        "id": conversation["id"],
        "text": format_conversation(conversation["messages"]),
        "metadata": conversation["metadata"]
    }