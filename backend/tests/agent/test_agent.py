import asyncio

from agent import agent as agent_module
from agent.agent import ask, ask_stream


async def _collect(agen):
    return [event async for event in agen]


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

    def test_agent_exception_logs_the_error(self, mocker, caplog):
        mocker.patch.object(agent_module, "Agent", side_effect=Exception("falha de rede"))

        with caplog.at_level("ERROR"):
            ask("meu pedido não chegou")

        assert "meu pedido não chegou" in caplog.text
        assert "falha de rede" in caplog.text


class TestAskStream:
    def test_yields_delta_event_per_chunk(self, mocker):
        async def fake_stream_async(question):
            yield {"data": "Olá"}
            yield {"data": " mundo"}

        fake_agent_instance = mocker.Mock()
        fake_agent_instance.stream_async = fake_stream_async
        fake_agent_instance.state.get.return_value = []
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        events = asyncio.run(_collect(ask_stream("oi")))

        assert events[0] == {"type": "delta", "text": "Olá"}
        assert events[1] == {"type": "delta", "text": " mundo"}

    def test_ignores_events_without_data(self, mocker):
        async def fake_stream_async(question):
            yield {"current_tool_use": {"name": "seek_knowledge"}}
            yield {"data": "resposta"}

        fake_agent_instance = mocker.Mock()
        fake_agent_instance.stream_async = fake_stream_async
        fake_agent_instance.state.get.return_value = []
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        events = asyncio.run(_collect(ask_stream("oi")))

        assert events == [
            {"type": "delta", "text": "resposta"},
            {"type": "done", "sources": []},
        ]

    def test_final_event_carries_sources(self, mocker):
        async def fake_stream_async(question):
            yield {"data": "resposta"}

        fake_agent_instance = mocker.Mock()
        fake_agent_instance.stream_async = fake_stream_async
        fake_agent_instance.state.get.return_value = [
            {"content": "conteudo", "similarity": 0.9}
        ]
        mocker.patch.object(agent_module, "Agent", return_value=fake_agent_instance)

        events = asyncio.run(_collect(ask_stream("oi")))

        assert events[-1] == {
            "type": "done",
            "sources": [{"content": "conteudo", "similarity": 0.9}],
        }

    def test_empty_question_yields_prompt_without_calling_agent(self, mocker):
        agent_spy = mocker.patch.object(agent_module, "Agent")

        events = asyncio.run(_collect(ask_stream("   ")))

        assert events == [
            {
                "type": "delta",
                "text": "Por favor, envie uma pergunta para que eu possa ajudar.",
            },
            {"type": "done", "sources": []},
        ]
        agent_spy.assert_not_called()

    def test_agent_exception_yields_error_event(self, mocker):
        mocker.patch.object(agent_module, "Agent", side_effect=Exception("falha de rede"))

        events = asyncio.run(_collect(ask_stream("meu pedido não chegou")))

        assert events == [
            {
                "type": "error",
                "message": (
                    "Desculpe, ocorreu um problema ao processar sua pergunta. "
                    "Tente novamente em instantes."
                ),
            }
        ]
