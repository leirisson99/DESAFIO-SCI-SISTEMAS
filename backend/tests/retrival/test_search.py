from retrival import search as search_module
from retrival.search import search_similarit_conversation


def _mock_connection(mocker, fetch_result):
    conn = mocker.Mock()
    cur = mocker.Mock()
    cur.fetchall.return_value = fetch_result
    conn.cursor.return_value = cur
    mocker.patch.object(search_module, "get_connection", return_value=conn)
    mocker.patch.object(search_module, "register_vector")
    return conn, cur


class TestSearchSimilaritConversation:
    def test_returns_empty_list_when_embedding_fails(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=None)
        get_connection_spy = mocker.patch.object(search_module, "get_connection")

        result = search_similarit_conversation("pergunta")

        assert result == []
        get_connection_spy.assert_not_called()

    def test_maps_rows_to_dicts(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=[0.1, 0.2])
        rows = [
            ("id1", "conteudo1", "duvida", "vendas", "neutro", 0.92),
            ("id2", "conteudo2", "reclamacao", "suporte", "negativo", 0.85),
        ]
        _mock_connection(mocker, rows)

        result = search_similarit_conversation("pergunta", k=2)

        assert result == [
            {
                "conversation_id": "id1",
                "content": "conteudo1",
                "intent": "duvida",
                "sector": "vendas",
                "sentiment": "neutro",
                "similarity": 0.92,
            },
            {
                "conversation_id": "id2",
                "content": "conteudo2",
                "intent": "reclamacao",
                "sector": "suporte",
                "sentiment": "negativo",
                "similarity": 0.85,
            },
        ]

    def test_calls_execute_with_embedding_and_k(self, mocker):
        embedding = [0.1, 0.2, 0.3]
        mocker.patch.object(search_module, "generation_embedding", return_value=embedding)
        _, cur = _mock_connection(mocker, [])

        search_similarit_conversation("pergunta", k=5)

        query, params = cur.execute.call_args[0]
        assert "SELECT" in query
        assert params == (embedding, embedding, 5)

    def test_empty_result_returns_empty_list(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=[0.1])
        _mock_connection(mocker, [])

        assert search_similarit_conversation("pergunta") == []

    def test_execute_exception_returns_empty_list(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=[0.1])
        _, cur = _mock_connection(mocker, [])
        cur.execute.side_effect = Exception("erro de banco")

        result = search_similarit_conversation("pergunta")

        assert result == []

    def test_connection_closed_after_success(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=[0.1])
        conn, _ = _mock_connection(mocker, [])

        search_similarit_conversation("pergunta")

        conn.close.assert_called_once()

    def test_connection_closed_after_failure(self, mocker):
        mocker.patch.object(search_module, "generation_embedding", return_value=[0.1])
        conn, cur = _mock_connection(mocker, [])
        cur.execute.side_effect = Exception("erro de banco")

        search_similarit_conversation("pergunta")

        conn.close.assert_called_once()
