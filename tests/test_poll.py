"""Tests for netlify/functions/poll.py"""
import json
import pytest
from unittest.mock import patch
from conftest import make_event, MemoryBlobs


@pytest.fixture(autouse=True)
def patch_blobs(mem_blobs):
    with patch("poll.blobs", mem_blobs):
        yield mem_blobs


class TestPollHandler:
    def test_pending_returns_202(self, patch_blobs):
        import poll
        patch_blobs.set_raw("tok1", {"status": "pending", "secret": None})
        resp = poll.handler(make_event(params={"token": "tok1"}), {})
        assert resp["statusCode"] == 202
        assert json.loads(resp["body"])["status"] == "pending"

    def test_approved_returns_200_with_secret(self, patch_blobs):
        import poll
        patch_blobs.set_raw("tok2", {"status": "approved", "secret": "s3cr3t"})
        resp = poll.handler(make_event(params={"token": "tok2"}), {})
        assert resp["statusCode"] == 200
        assert json.loads(resp["body"])["secret"] == "s3cr3t"

    def test_approved_burns_token(self, patch_blobs):
        import poll
        patch_blobs.set_raw("tok3", {"status": "approved", "secret": "val"})
        poll.handler(make_event(params={"token": "tok3"}), {})
        assert patch_blobs.get("tok3") is None

    def test_denied_returns_403(self, patch_blobs):
        import poll
        patch_blobs.set_raw("tok4", {"status": "denied", "secret": None})
        resp = poll.handler(make_event(params={"token": "tok4"}), {})
        assert resp["statusCode"] == 403

    def test_denied_burns_token(self, patch_blobs):
        import poll
        patch_blobs.set_raw("tok5", {"status": "denied", "secret": None})
        poll.handler(make_event(params={"token": "tok5"}), {})
        assert patch_blobs.get("tok5") is None

    def test_unknown_token_returns_404(self):
        import poll
        resp = poll.handler(make_event(params={"token": "ghost"}), {})
        assert resp["statusCode"] == 404

    def test_missing_token_param_returns_400(self):
        import poll
        resp = poll.handler(make_event(), {})
        assert resp["statusCode"] == 400

    def test_post_method_returns_405(self):
        import poll
        resp = poll.handler(make_event(method="POST", params={"token": "x"}), {})
        assert resp["statusCode"] == 405
