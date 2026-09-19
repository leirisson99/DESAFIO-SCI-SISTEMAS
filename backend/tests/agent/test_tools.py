from agent import tools as tools_module
from agent.tools import seek_knowledge


class TestSeekKnowledge:
    def test_returns_fallback_message_when_no_results(self, mocker):
        mocker.patch.object(tools_module, "search_similarit_conversation", return_value=[])

        result = seek_knowledge("meu pedido não chegou")

        assert result == (
            "Nenhuma informação relevante foi encontrada na base de conhecimento "
            "para essa pergunta."
        )

    def test_calls_search_with_the_question(self, mocker):
        spy = mocker.patch.object(
            tools_module, "search_similarit_conversation", return_value=[]
        )

        seek_knowledge("qual o prazo de entrega?")

        spy.assert_called_once_with("qual o prazo de entrega?")

    def test_formats_single_result(self, mocker):
        mocker.patch.object(
            tools_module,
            "search_similarit_conversation",
            return_value=[
                {
                    "conversation_id": "abc123",
                    "content": "cliente perguntou sobre o pedido",
                    "intent": "duvida",
                    "sector": "logistica",
                    "sentiment": "neutro",
                    "similarity": 0.876,
                }
            ],
        )

        result = seek_knowledge("meu pedido não chegou")

        assert result == (
            "[Conversa abc123 | setor: logistica | similaridade: 0.88]\n"
            "cliente perguntou sobre o pedido"
        )

    def test_joins_multiple_results_with_separator(self, mocker):
        mocker.patch.object(
            tools_module,
            "search_similarit_conversation",
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

        result = seek_knowledge("pergunta qualquer")

        assert "---" in result
        assert result.index("id1") < result.index("id2")
