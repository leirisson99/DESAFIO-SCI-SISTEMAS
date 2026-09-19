import pytest

from ingestion import setup_db as setup_db_module


class TestGetConnection:
    def test_raises_when_database_url_missing(self, mocker):
        mocker.patch.object(setup_db_module.os, "getenv", return_value=None)
        with pytest.raises(ValueError):
            setup_db_module.get_connection()

    def test_calls_psycopg2_connect_with_url(self, mocker):
        mocker.patch.object(
            setup_db_module.os, "getenv", return_value="postgresql://user:pass@host/db"
        )
        connect_spy = mocker.patch.object(setup_db_module.psycopg2, "connect")

        setup_db_module.get_connection()

        connect_spy.assert_called_once_with("postgresql://user:pass@host/db")


class TestCreateTable:
    def _mock_connection(self, mocker):
        conn = mocker.Mock()
        cur = mocker.Mock()
        conn.cursor.return_value = cur
        mocker.patch.object(setup_db_module, "get_connection", return_value=conn)
        return conn, cur

    def test_success_commits(self, mocker):
        conn, cur = self._mock_connection(mocker)

        setup_db_module.create_table()

        conn.commit.assert_called_once()

    def test_exception_rolls_back(self, mocker):
        conn, cur = self._mock_connection(mocker)
        cur.execute.side_effect = Exception("erro de banco")

        setup_db_module.create_table()

        conn.rollback.assert_called_once()
