"""Tests for netlify/functions/details.py"""
import json
import pytest
from unittest.mock import patch
from conftest import make_event, MemoryBlobs


@pytest.fixture(autouse=True)
def patch_blobs(mem_blobs):
    with patch("details.blobs", mem_blobs):
        yield mem_blobs


class TestDetailsHandler:
    def test_returns_metadata_for_valid_token(self, patch_blobs):
        import details
        patch_blobs.set_raw("tok1", {
            "label": "GITHUB_ACCESS_TOKEN",
            "status": "pending",
            "created_at": "2026-01-01T00:00:00+00:00",
        })
        resp = details.handler(make_event(params={"token": "tok1"}), {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["label"] == "GITHUB_ACCESS_TOKEN"
        assert body["status"] == "pending"

    def test_does_not_expose_secret(self, patch_blobs):
        import details
        patch_blobs.set_raw("tok2", {
            "label": "X",
            "status": "approved",
            "secret": "supersecret",
            "created_at": "2026-01-01T00:00:00+00:00",
        })
        resp = details.handler(make_event(params={"token": "tok2"}), {})
        body = json.loads(resp["body"])
        assert "secret" not in body

    def test_missing_token_returns_400(self):
        import details
        resp = details.handler(make_event(), {})
        assert resp["statusCode"] == 400

    def test_unknown_token_returns_404(self):
        import details
        resp = details.handler(make_event(params={"token": "ghost"}), {})
        assert resp["statusCode"] == 404

    def test_post_method_returns_405(self):
        import details
        resp = details.handler(make_event(method="POST"), {})
        assert resp["statusCode"] == 405
