from fastapi import FastAPI

from observability import setup_observability


class TestSetupObservability:
    def test_does_not_raise_without_otel_env_vars(self, monkeypatch, mocker):
        monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
        monkeypatch.delenv("OTEL_SERVICE_NAME", raising=False)
        mocker.patch("observability.openlit.init")

        app = FastAPI()
        setup_observability(app)

        paths = [route.path for route in app.routes]
        assert "/metrics" in paths

    def test_openlit_failure_does_not_crash_startup(self, mocker):
        mocker.patch("observability.openlit.init", side_effect=Exception("sem conexão"))

        app = FastAPI()
        setup_observability(app)

        paths = [route.path for route in app.routes]
        assert "/metrics" in paths
