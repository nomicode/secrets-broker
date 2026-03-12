"""Tests for netlify/functions/request.py"""
import json
import pytest
from unittest.mock import patch
from conftest import make_event, MemoryBlobs


@pytest.fixture(autouse=True)
def patch_blobs(mem_blobs):
    with patch("request.blobs", mem_blobs):
        yield mem_blobs


class TestRequestHandler:
    def test_valid_request_returns_token_and_urls(self, patch_blobs):
        import request
        event = make_event(method="POST", body=json.dumps({"label": "GITHUB_ACCESS_TOKEN"}))
        resp = request.handler(event, {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert "token" in body
        assert "form_url" in body
        assert "poll_url" in body
        assert body["token"] in body["form_url"]

    def test_pending_record_stored_in_blobs(self, patch_blobs):
        import request
        event = make_event(method="POST", body=json.dumps({"label": "GITHUB_ACCESS_TOKEN"}))
        resp = request.handler(event, {})
        token = json.loads(resp["body"])["token"]
        record = patch_blobs.get(token)
        assert record is not None
        assert record["status"] == "pending"
        assert record["label"] == "GITHUB_ACCESS_TOKEN"

    def test_missing_label_returns_400(self):
        import request
        event = make_event(method="POST", body=json.dumps({}))
        resp = request.handler(event, {})
        assert resp["statusCode"] == 400

    def test_empty_label_returns_400(self):
        import request
        event = make_event(method="POST", body=json.dumps({"label": "  "}))
        resp = request.handler(event, {})
        assert resp["statusCode"] == 400

    def test_invalid_json_returns_400(self):
        import request
        event = make_event(method="POST", body="not json")
        resp = request.handler(event, {})
        assert resp["statusCode"] == 400

    def test_get_method_returns_405(self):
        import request
        resp = request.handler(make_event(method="GET"), {})
        assert resp["statusCode"] == 405

    def test_callback_url_stored(self, patch_blobs):
        import request
        event = make_event(
            method="POST",
            body=json.dumps({"label": "HF_TOKEN", "callback_url": "https://example.com/cb"}),
        )
        resp = request.handler(event, {})
        token = json.loads(resp["body"])["token"]
        assert patch_blobs.get(token)["callback_url"] == "https://example.com/cb"

    def test_each_request_gets_unique_token(self, patch_blobs):
        import request
        def make():
            e = make_event(method="POST", body=json.dumps({"label": "X"}))
            return json.loads(request.handler(e, {})["body"])["token"]
        assert make() != make()
