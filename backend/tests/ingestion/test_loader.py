import pytest

from ingestion.loader import format_conversation, preparation_conversation


class TestFormatConversation:
    def test_empty_messages_returns_empty_string(self):
        assert format_conversation([]) == ""

    def test_formats_role_and_content(self):
        messages = [
            {"role": "user", "content": "Olá"},
            {"role": "assistant", "content": "Como posso ajudar?"},
        ]
        assert format_conversation(messages) == (
            "user : Olá\nassistant : Como posso ajudar?"
        )

    def test_skips_messages_with_empty_content(self):
        messages = [
            {"role": "user", "content": "  "},
            {"role": "assistant", "content": "Tudo bem"},
        ]
        assert format_conversation(messages) == "assistant : Tudo bem"

    def test_missing_role_defaults_to_desconhecido(self):
        messages = [{"content": "sem role"}]
        assert format_conversation(messages) == "desconhecido : sem role"

    def test_strips_whitespace_from_content(self):
        messages = [{"role": "user", "content": "  espacos  "}]
        assert format_conversation(messages) == "user : espacos"


class TestPreparationConversation:
    def test_builds_expected_dict(self):
        conversation = {
            "id": "abc123",
            "messages": [{"role": "user", "content": "oi"}],
            "metadata": {"intent": "duvida"},
        }
        result = preparation_conversation(conversation)
        assert result == {
            "id": "abc123",
            "text": "user : oi",
            "metadata": {"intent": "duvida"},
        }

    def test_empty_messages_produces_empty_text(self):
        conversation = {"id": "abc123", "messages": [], "metadata": {}}
        result = preparation_conversation(conversation)
        assert result["text"] == ""

    def test_missing_id_raises_key_error(self):
        conversation = {"messages": [], "metadata": {}}
        with pytest.raises(KeyError):
            preparation_conversation(conversation)

    def test_missing_metadata_raises_key_error(self):
        conversation = {"id": "abc123", "messages": []}
        with pytest.raises(KeyError):
            preparation_conversation(conversation)
