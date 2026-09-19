from agent.prompts import SYSTEM_PROMPT


class TestSystemPrompt:
    def test_is_a_non_empty_string(self):
        assert isinstance(SYSTEM_PROMPT, str)
        assert SYSTEM_PROMPT.strip() != ""

    def test_instructs_to_admit_missing_information(self):
        assert "não possui informação suficiente" in SYSTEM_PROMPT

    def test_instructs_to_not_expose_internal_details(self):
        assert "IDs de conversa" in SYSTEM_PROMPT
