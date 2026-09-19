from agent import agent as agent_module
from agent.agent import ask


class TestAsk:
    def test_returns_string_of_agent_response(self, mocker):
        fake_agent_instance = mocker.Mock(return_value="resposta do agente")
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        result = ask("meu pedido não chegou, o que faço?")

        assert result == "resposta do agente"

    def test_calls_agent_with_the_question(self, mocker):
        fake_agent_instance = mocker.Mock(return_value="ok")
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        ask("qual o prazo de entrega?")

        fake_agent_instance.assert_called_once_with("qual o prazo de entrega?")

    def test_casts_non_string_response_to_string(self, mocker):
        fake_response = mocker.Mock()
        fake_response.__str__ = mocker.Mock(return_value="texto formatado")
        fake_agent_instance = mocker.Mock(return_value=fake_response)
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        result = ask("pergunta qualquer")

        assert result == "texto formatado"

    def test_creates_a_new_agent_instance_per_call(self, mocker):
        agent_class_spy = mocker.patch.object(
            agent_module, "Agent", return_value=mocker.Mock(return_value="ok")
        )

        ask("primeira pergunta")
        ask("segunda pergunta")

        assert agent_class_spy.call_count == 2

    def test_empty_string_returns_prompt_without_calling_agent(self, mocker):
        agent_spy = mocker.patch.object(agent_module, "Agent")

        result = ask("")

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        agent_spy.assert_not_called()

    def test_whitespace_only_returns_prompt_without_calling_agent(self, mocker):
        agent_spy = mocker.patch.object(agent_module, "Agent")

        result = ask("   ")

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        agent_spy.assert_not_called()

    def test_none_question_returns_prompt_without_calling_agent(self, mocker):
        agent_spy = mocker.patch.object(agent_module, "Agent")

        result = ask(None)

        assert result == "Por favor, envie uma pergunta para que eu possa ajudar."
        agent_spy.assert_not_called()

    def test_agent_exception_returns_friendly_message(self, mocker):
        mocker.patch.object(agent_module, "Agent", side_effect=Exception("falha de rede"))

        result = ask("meu pedido não chegou")

        assert result == (
            "Desculpe, ocorreu um problema ao processar sua pergunta. "
            "Tente novamente em instantes."
        )

    def test_agent_exception_logs_the_error(self, mocker, capsys):
        mocker.patch.object(agent_module, "Agent", side_effect=Exception("falha de rede"))

        ask("meu pedido não chegou")

        captured = capsys.readouterr()
        assert "meu pedido não chegou" in captured.out
        assert "falha de rede" in captured.out
