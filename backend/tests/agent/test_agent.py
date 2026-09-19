from agent import agent as agent_module
from agent.agent import ask


class TestAsk:
    def test_returns_string_of_agent_response(self, mocker):
        mocker.patch.object(agent_module, "agent", return_value="resposta do agente")

        result = ask("meu pedido não chegou, o que faço?")

        assert result == "resposta do agente"

    def test_calls_agent_with_the_question(self, mocker):
        spy = mocker.patch.object(agent_module, "agent", return_value="ok")

        ask("qual o prazo de entrega?")

        spy.assert_called_once_with("qual o prazo de entrega?")

    def test_casts_non_string_response_to_string(self, mocker):
        fake_response = mocker.Mock()
        fake_response.__str__ = mocker.Mock(return_value="texto formatado")
        mocker.patch.object(agent_module, "agent", return_value=fake_response)

        result = ask("pergunta qualquer")

        assert result == "texto formatado"

    def test_empty_string_returns_prompt_without_calling_agent(self, mocker):
        spy = mocker.patch.object(agent_module, "agent")

        result = ask("")

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        spy.assert_not_called()

    def test_whitespace_only_returns_prompt_without_calling_agent(self, mocker):
        spy = mocker.patch.object(agent_module, "agent")

        result = ask("   ")

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        spy.assert_not_called()

    def test_none_question_returns_prompt_without_calling_agent(self, mocker):
        spy = mocker.patch.object(agent_module, "agent")

        result = ask(None)

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        spy.assert_not_called()

    def test_agent_exception_returns_friendly_message(self, mocker):
        mocker.patch.object(agent_module, "agent", side_effect=Exception("falha de rede"))

        result = ask("meu pedido não chegou")

        assert result == (
            "Desculpe, ocorreu um problema ao processar sua pergunta. "
            "Tente novamente em instantes."
        )

    def test_agent_exception_logs_the_error(self, mocker, capsys):
        mocker.patch.object(agent_module, "agent", side_effect=Exception("falha de rede"))

        ask("meu pedido não chegou")

        captured = capsys.readouterr()
        assert "meu pedido não chegou" in captured.out
        assert "falha de rede" in captured.out
