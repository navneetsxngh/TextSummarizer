"""
Unit tests for the FastAPI application.

The ML prediction pipeline (PredictionPipeline) is mocked so that
these tests run fast in CI without downloading PyTorch models.
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# ── Import app with heavy ML imports mocked ───────────────────────────────────
# This must happen before `from app import app` so the import side-effects
# (model loading) are never triggered in CI.
import sys

# Stub out the heavy ML modules that would fail in a minimal CI environment
for mod in [
    "torch",
    "transformers",
    "datasets",
    "sacrebleu",
    "rouge_score",
    "nltk",
    "pandas",
    "seaborn",
    "matplotlib",
    "matplotlib.pyplot",
    "py7zr",
    "boto3",
    "mypy_boto3_s3",
]:
    sys.modules.setdefault(mod, MagicMock())

from app import app  # noqa: E402  (must be after stubs)

client = TestClient(app)


# ══════════════════════════════════════════════════════════════════════════════
#  HOME ROUTE
# ══════════════════════════════════════════════════════════════════════════════
class TestHomeRoute:
    def test_home_returns_200(self):
        response = client.get("/")
        assert response.status_code == 200

    def test_home_returns_html(self):
        response = client.get("/")
        assert "text/html" in response.headers["content-type"]

    def test_home_contains_app_title(self):
        response = client.get("/")
        assert "AI Text Summarizer" in response.text


# ══════════════════════════════════════════════════════════════════════════════
#  TRAIN ROUTES
# ══════════════════════════════════════════════════════════════════════════════
class TestTrainRoutes:
    def test_train_page_returns_200(self):
        response = client.get("/train")
        assert response.status_code == 200

    def test_train_page_returns_html(self):
        response = client.get("/train")
        assert "text/html" in response.headers["content-type"]

    def test_train_status_default_is_idle(self):
        # Reset state first
        client.post("/train/reset")
        response = client.get("/train/status")
        assert response.status_code == 200
        data = response.json()
        assert data["running"] is False
        assert data["completed"] is False
        assert data["error"] is None

    def test_train_reset_clears_state(self):
        response = client.post("/train/reset")
        assert response.status_code == 200
        assert response.json()["status"] == "reset"

    def test_train_status_after_reset(self):
        client.post("/train/reset")
        data = client.get("/train/status").json()
        assert data["logs"] == []
        assert data["running"] is False


# ══════════════════════════════════════════════════════════════════════════════
#  PREDICT ROUTES
# ══════════════════════════════════════════════════════════════════════════════
class TestPredictRoutes:
    def test_predict_page_returns_200(self):
        response = client.get("/predict")
        assert response.status_code == 200

    def test_predict_page_returns_html(self):
        response = client.get("/predict")
        assert "text/html" in response.headers["content-type"]

    def test_predict_empty_text_returns_400(self):
        response = client.post("/predict", json={"text": ""})
        assert response.status_code == 400
        assert "error" in response.json()

    def test_predict_missing_text_key_returns_400(self):
        response = client.post("/predict", json={})
        assert response.status_code == 400

    def test_predict_whitespace_only_returns_400(self):
        response = client.post("/predict", json={"text": "   \n\t  "})
        assert response.status_code == 400

    def test_predict_success_with_mocked_pipeline(self):
        mock_summary = "This is a mocked AI summary."

        with patch("app.PredictionPipeline") as MockPipeline:
            instance = MockPipeline.return_value
            instance.predict.return_value = mock_summary

            response = client.post(
                "/predict",
                json={"text": "This is a long article about AI and text summarization."},
            )

        assert response.status_code == 200
        assert response.json()["summary"] == mock_summary

    def test_predict_pipeline_error_returns_500(self):
        with patch("app.PredictionPipeline") as MockPipeline:
            instance = MockPipeline.return_value
            instance.predict.side_effect = RuntimeError("Model not found")

            response = client.post(
                "/predict",
                json={"text": "Some text to summarize for testing purposes."},
            )

        assert response.status_code == 500
        assert "error" in response.json()


# ══════════════════════════════════════════════════════════════════════════════
#  STATIC FILES
# ══════════════════════════════════════════════════════════════════════════════
class TestStaticFiles:
    def test_css_file_is_served(self):
        response = client.get("/static/css/style.css")
        assert response.status_code == 200
        assert "text/css" in response.headers["content-type"]

    def test_js_file_is_served(self):
        response = client.get("/static/js/app.js")
        assert response.status_code == 200

    def test_missing_static_file_returns_404(self):
        response = client.get("/static/nonexistent.xyz")
        assert response.status_code == 404


# ══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ══════════════════════════════════════════════════════════════════════════════
class TestEdgeCases:
    def test_unknown_route_returns_404(self):
        response = client.get("/nonexistent-route")
        assert response.status_code == 404

    def test_predict_accepts_long_text(self):
        long_text = "AI is transforming industries. " * 100  # 3100 chars

        with patch("app.PredictionPipeline") as MockPipeline:
            instance = MockPipeline.return_value
            instance.predict.return_value = "Long text summary."
            response = client.post("/predict", json={"text": long_text})

        assert response.status_code == 200

    def test_train_start_idempotent_while_running(self):
        """Starting training twice should return 409 on the second call."""
        import app as app_module

        # Manually set running state to simulate an in-progress training
        original = app_module._training.copy()
        app_module._training["running"] = True
        try:
            response = client.post("/train/start")
            assert response.status_code == 409
        finally:
            app_module._training.update(original)
