"""Tests for netlify/functions/submit.py"""
import json
import pytest
from unittest.mock import patch, MagicMock
from conftest import make_event, MemoryBlobs, identity_ok, identity_fail


AUTHED = {"authorization": "Bearer valid-jwt"}


@pytest.fixture(autouse=True)
def patch_blobs(mem_blobs):
    with patch("submit.blobs", mem_blobs):
        yield mem_blobs


@pytest.fixture(autouse=True)
def patch_identity_ok():
    mock_resp = identity_ok()
    with patch("submit._r.get", return_value=mock_resp):
        yield


class TestSubmitApprove:
    def test_approve_sets_status_approved(self, patch_blobs):
        import submit
        patch_blobs.set_raw("tok1", {"status": "pending", "label": "GITHUB_ACCESS_TOKEN", "callback_url": ""})
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "tok1", "action": "approve", "secret": "ghp_abc"}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 200
        assert patch_blobs.get("tok1")["status"] == "approved"
        assert patch_blobs.get("tok1")["secret"] == "ghp_abc"

    def test_deny_sets_status_denied(self, patch_blobs):
        import submit
        patch_blobs.set_raw("tok2", {"status": "pending", "label": "X", "callback_url": ""})
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "tok2", "action": "deny", "secret": ""}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 200
        assert patch_blobs.get("tok2")["status"] == "denied"
        assert patch_blobs.get("tok2")["secret"] is None

    def test_callback_url_fired_on_approve(self, patch_blobs):
        import submit
        patch_blobs.set_raw("tok3", {
            "status": "pending", "label": "X",
            "callback_url": "https://example.com/cb",
        })
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "tok3", "action": "approve", "secret": "val"}),
        )
        with patch("submit._r.post") as mock_post:
            submit.handler(event, {})
            mock_post.assert_called_once()
            call_kwargs = mock_post.call_args
            assert call_kwargs[0][0] == "https://example.com/cb"

    def test_callback_url_not_fired_on_deny(self, patch_blobs):
        import submit
        patch_blobs.set_raw("tok4", {
            "status": "pending", "label": "X",
            "callback_url": "https://example.com/cb",
        })
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "tok4", "action": "deny", "secret": ""}),
        )
        with patch("submit._r.post") as mock_post:
            submit.handler(event, {})
            mock_post.assert_not_called()


class TestSubmitAuth:
    def test_no_auth_header_returns_401(self):
        import submit
        with patch("submit._r.get", return_value=identity_fail()):
            event = make_event(
                method="POST",
                body=json.dumps({"token": "x", "action": "approve", "secret": "v"}),
            )
            resp = submit.handler(event, {})
            assert resp["statusCode"] == 401

    def test_invalid_jwt_returns_401(self):
        import submit
        with patch("submit._r.get", return_value=identity_fail()):
            event = make_event(
                method="POST",
                headers={"authorization": "Bearer bad-token"},
                body=json.dumps({"token": "x", "action": "approve", "secret": "v"}),
            )
            resp = submit.handler(event, {})
            assert resp["statusCode"] == 401


class TestSubmitValidation:
    def test_missing_token_returns_400(self):
        import submit
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"action": "approve", "secret": "v"}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 400

    def test_invalid_action_returns_400(self):
        import submit
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "x", "action": "maybe", "secret": "v"}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 400

    def test_unknown_token_returns_404(self):
        import submit
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "ghost", "action": "approve", "secret": "v"}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 404

    def test_already_resolved_returns_409(self, patch_blobs):
        import submit
        patch_blobs.set_raw("tok5", {"status": "approved", "label": "X", "callback_url": ""})
        event = make_event(
            method="POST",
            headers=AUTHED,
            body=json.dumps({"token": "tok5", "action": "approve", "secret": "v"}),
        )
        resp = submit.handler(event, {})
        assert resp["statusCode"] == 409

    def test_get_method_returns_405(self):
        import submit
        resp = submit.handler(make_event(method="GET"), {})
        assert resp["statusCode"] == 405
