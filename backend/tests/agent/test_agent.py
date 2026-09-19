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
