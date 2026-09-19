from ingestion import insert_conversation as insert_conversation_module
from ingestion.insert_conversation import insert_conversation


def _mock_connection(mocker):
    conn = mocker.Mock()
    cur = mocker.Mock()
    conn.cursor.return_value = cur
    mocker.patch.object(insert_conversation_module, "get_connection", return_value=conn)
    mocker.patch.object(insert_conversation_module, "register_vector")
    return conn, cur


class TestInsertConversation:
    def test_insert_success_returns_true(self, mocker):
        conn, cur = _mock_connection(mocker)

        result = insert_conversation(
            conversation_id="abc123",
            content="texto",
            embedding=[0.1, 0.2],
            intent="duvida",
            sector="vendas",
            sentiment="neutro",
        )

        assert result is True
        conn.commit.assert_called_once()

    def test_insert_calls_execute_with_correct_params(self, mocker):
        conn, cur = _mock_connection(mocker)

        insert_conversation(
            conversation_id="abc123",
            content="texto",
            embedding=[0.1, 0.2],
            intent="duvida",
            sector="vendas",
            sentiment="neutro",
        )

        query, params = cur.execute.call_args[0]
        assert "INSERT INTO conversation" in query
        assert params == ("abc123", "texto", [0.1, 0.2], "duvida", "vendas", "neutro")

    def test_insert_conflict_does_nothing_but_still_returns_true(self, mocker):
        conn, cur = _mock_connection(mocker)

        result = insert_conversation(
            conversation_id="dup",
            content="texto",
            embedding=[0.1],
            intent=None,
            sector=None,
            sentiment=None,
        )

        query, _ = cur.execute.call_args[0]
        assert "ON CONFLICT (conversation_id) DO NOTHING" in query
        assert result is True

    def test_execute_exception_rolls_back_and_returns_false(self, mocker):
        conn, cur = _mock_connection(mocker)
        cur.execute.side_effect = Exception("erro de banco")

        result = insert_conversation(
            conversation_id="abc123",
            content="texto",
            embedding=[0.1],
            intent="duvida",
            sector="vendas",
            sentiment="neutro",
        )

        conn.rollback.assert_called_once()
        assert result is False

    def test_connection_closed_on_success(self, mocker):
        conn, cur = _mock_connection(mocker)

        insert_conversation(
            conversation_id="abc123",
            content="texto",
            embedding=[0.1],
            intent="duvida",
            sector="vendas",
            sentiment="neutro",
        )

        conn.close.assert_called()

    def test_connection_closed_on_failure(self, mocker):
        conn, cur = _mock_connection(mocker)
        cur.execute.side_effect = Exception("erro de banco")

        insert_conversation(
            conversation_id="abc123",
            content="texto",
            embedding=[0.1],
            intent="duvida",
            sector="vendas",
            sentiment="neutro",
        )

        conn.close.assert_called()
