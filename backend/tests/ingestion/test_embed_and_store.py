from ingestion import embed_and_store


class TestGenerationEmbedding:
    def test_empty_text_returns_none_without_calling_api(self, mocker):
        spy = mocker.patch.object(embed_and_store.client.embeddings, "create")
        assert embed_and_store.generation_embedding("") is None
        spy.assert_not_called()

    def test_whitespace_only_text_returns_none(self, mocker):
        spy = mocker.patch.object(embed_and_store.client.embeddings, "create")
        assert embed_and_store.generation_embedding("   ") is None
        spy.assert_not_called()

    def test_valid_text_returns_embedding_vector(self, mocker):
        fake_embedding = [0.1, 0.2, 0.3]
        fake_response = mocker.Mock()
        fake_response.data = [mocker.Mock(embedding=fake_embedding)]
        mocker.patch.object(
            embed_and_store.client.embeddings, "create", return_value=fake_response
        )

        result = embed_and_store.generation_embedding("texto valido")

        assert result == fake_embedding

    def test_api_exception_returns_none(self, mocker):
        mocker.patch.object(
            embed_and_store.client.embeddings,
            "create",
            side_effect=Exception("falha na API"),
        )
        assert embed_and_store.generation_embedding("texto valido") is None
