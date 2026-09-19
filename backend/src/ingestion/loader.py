


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