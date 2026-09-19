from fastapi.middleware.cors import CORSMiddleware
from fastapi.testclient import TestClient

from api import main as api_main_module
from api.main import parse_allowed_origins

client = TestClient(api_main_module.app)


class TestChatEndpoint:
    def test_happy_path_returns_answer_and_sources(self, mocker):
        mocker.patch.object(api_main_module, "ask", return_value="Resposta do agente")
        mocker.patch.object(
            api_main_module,
            "get_ultimos_resultados",
            return_value=[
                {
                    "conversation_id": "abc123",
                    "content": "conteudo da conversa",
                    "intent": "duvida",
                    "sector": "logistica",
                    "sentiment": "neutro",
                    "similarity": 0.87,
                }
            ],
        )

        response = client.post("/chat", json={"message": "meu pedido não chegou"})

        assert response.status_code == 200
        assert response.json() == {
            "answer": "Resposta do agente",
            "sources": [
                {
                    "conversation_id": "abc123",
                    "content": "conteudo da conversa",
                    "intent": "duvida",
                    "sector": "logistica",
                    "sentiment": "neutro",
                    "similarity": 0.87,
                }
            ],
        }

    def test_empty_sources_list(self, mocker):
        mocker.patch.object(api_main_module, "ask", return_value="Resposta do agente")
        mocker.patch.object(api_main_module, "get_ultimos_resultados", return_value=[])

        response = client.post("/chat", json={"message": "qual a capital da França?"})

        assert response.status_code == 200
        assert response.json()["sources"] == []

    def test_calls_ask_with_the_message(self, mocker):
        spy = mocker.patch.object(api_main_module, "ask", return_value="ok")
        mocker.patch.object(api_main_module, "get_ultimos_resultados", return_value=[])

        client.post("/chat", json={"message": "qual o prazo de entrega?"})

        spy.assert_called_once_with("qual o prazo de entrega?")

    def test_calls_get_ultimos_resultados_after_asking(self, mocker):
        mocker.patch.object(api_main_module, "ask", return_value="ok")
        spy = mocker.patch.object(
            api_main_module, "get_ultimos_resultados", return_value=[]
        )

        client.post("/chat", json={"message": "qual o prazo de entrega?"})

        spy.assert_called_once_with()

    def test_missing_message_field_returns_422(self, mocker):
        ask_spy = mocker.patch.object(api_main_module, "ask")
        sources_spy = mocker.patch.object(api_main_module, "get_ultimos_resultados")

        response = client.post("/chat", json={})

        assert response.status_code == 422
        ask_spy.assert_not_called()
        sources_spy.assert_not_called()

    def test_empty_message_still_returns_200(self, mocker):
        mocker.patch.object(
            api_main_module,
            "ask",
            return_value="Por favor, envie uma pergunta para que eu possa ajudar.",
        )
        mocker.patch.object(api_main_module, "get_ultimos_resultados", return_value=[])

        response = client.post("/chat", json={"message": ""})

        assert response.status_code == 200
        assert response.json()["answer"] == (
            "Por favor, envie uma pergunta para que eu possa ajudar."
        )

    def test_wrong_type_for_message_returns_422(self, mocker):
        ask_spy = mocker.patch.object(api_main_module, "ask")
        sources_spy = mocker.patch.object(api_main_module, "get_ultimos_resultados")

        response = client.post("/chat", json={"message": 123})

        assert response.status_code == 422
        ask_spy.assert_not_called()
        sources_spy.assert_not_called()

    def test_multiple_sources_preserve_order(self, mocker):
        mocker.patch.object(api_main_module, "ask", return_value="ok")
        mocker.patch.object(
            api_main_module,
            "get_ultimos_resultados",
            return_value=[
                {
                    "conversation_id": "id1",
                    "content": "conteudo 1",
                    "intent": "duvida",
                    "sector": "vendas",
                    "sentiment": "neutro",
                    "similarity": 0.9,
                },
                {
                    "conversation_id": "id2",
                    "content": "conteudo 2",
                    "intent": "reclamacao",
                    "sector": "suporte",
                    "sentiment": "negativo",
                    "similarity": 0.8,
                },
            ],
        )

        response = client.post("/chat", json={"message": "pergunta qualquer"})

        sources = response.json()["sources"]
        assert [s["conversation_id"] for s in sources] == ["id1", "id2"]


class TestParseAllowedOrigins:
    def test_empty_string_returns_empty_list(self):
        assert parse_allowed_origins("") == []

    def test_single_origin(self):
        assert parse_allowed_origins("http://localhost:3000") == [
            "http://localhost:3000"
        ]

    def test_multiple_origins_split_by_comma(self):
        assert parse_allowed_origins(
            "http://localhost:3000,http://localhost:5173"
        ) == ["http://localhost:3000", "http://localhost:5173"]

    def test_strips_whitespace_around_each_origin(self):
        assert parse_allowed_origins(
            " http://localhost:3000 , http://localhost:5173 "
        ) == ["http://localhost:3000", "http://localhost:5173"]

    def test_ignores_empty_segments_from_trailing_comma(self):
        assert parse_allowed_origins("http://localhost:3000,") == [
            "http://localhost:3000"
        ]


class TestCORSConfiguration:
    def test_cors_middleware_is_registered(self):
        middleware_classes = [m.cls for m in api_main_module.app.user_middleware]
        assert CORSMiddleware in middleware_classes

    def test_cors_middleware_uses_parsed_allowed_origins(self):
        cors_middleware = next(
            m
            for m in api_main_module.app.user_middleware
            if m.cls is CORSMiddleware
        )
        assert cors_middleware.kwargs["allow_origins"] == api_main_module.ALLOWED_ORIGINS
