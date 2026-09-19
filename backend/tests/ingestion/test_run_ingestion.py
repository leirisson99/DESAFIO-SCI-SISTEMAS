import json

import pytest

from ingestion.run_ingestion import load_conversations


class TestLoadConversations:
    def test_parses_valid_jsonl(self, tmp_path):
        path = tmp_path / "conversations.jsonl"
        rows = [
            {"id": "1", "messages": [{"role": "user", "content": "oi"}], "metadata": {}},
            {"id": "2", "messages": [{"role": "user", "content": "ola"}], "metadata": {}},
        ]
        path.write_text(
            "\n".join(json.dumps(row) for row in rows), encoding="utf-8"
        )

        result = load_conversations(str(path))

        assert result == rows

    def test_empty_file_returns_empty_list(self, tmp_path):
        path = tmp_path / "conversations.jsonl"
        path.write_text("", encoding="utf-8")

        assert load_conversations(str(path)) == []

    def test_invalid_json_line_raises(self, tmp_path):
        path = tmp_path / "conversations.jsonl"
        path.write_text("{invalido}", encoding="utf-8")

        with pytest.raises(json.JSONDecodeError):
            load_conversations(str(path))
