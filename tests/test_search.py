"""Tests for netlify/functions/search.py"""
import json
import pytest
from conftest import make_event


class TestSearchHandler:
    def test_no_params_returns_all(self):
        import search
        resp = search.handler(make_event(), {})
        assert resp["statusCode"] == 200
        body = json.loads(resp["body"])
        assert body["total"] == 5  # all registry entries
        assert len(body["results"]) == 5

    def test_name_hf_returns_huggingface(self):
        import search
        resp = search.handler(make_event(params={"name": "hf"}), {})
        keys = [r["key"] for r in json.loads(resp["body"])["results"]]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys

    def test_name_or_terms(self):
        import search
        resp = search.handler(make_event(params={"name": "hf or claude"}), {})
        keys = [r["key"] for r in json.loads(resp["body"])["results"]]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys
        assert "CLAUDE_ACCESS_TOKEN" in keys

    def test_scope_ml_glob(self):
        import search
        resp = search.handler(make_event(params={"scope": "ml.*"}), {})
        keys = [r["key"] for r in json.loads(resp["body"])["results"]]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys
        assert "GITHUB_ACCESS_TOKEN" not in keys

    def test_scope_wildcard_returns_all(self):
        import search
        resp = search.handler(make_event(params={"scope": "*"}), {})
        assert json.loads(resp["body"])["total"] == 5

    def test_name_and_scope_combined(self):
        import search
        resp = search.handler(make_event(params={"name": "github", "scope": "vcs.*"}), {})
        keys = [r["key"] for r in json.loads(resp["body"])["results"]]
        assert "GITHUB_ACCESS_TOKEN" in keys

    def test_name_and_scope_mismatch_returns_empty(self):
        import search
        resp = search.handler(make_event(params={"name": "slack", "scope": "ml.*"}), {})
        assert json.loads(resp["body"])["total"] == 0

    def test_garbage_name_returns_empty(self):
        import search
        resp = search.handler(make_event(params={"name": "xyzzy-no-match"}), {})
        assert json.loads(resp["body"])["total"] == 0

    def test_results_never_include_secret_values(self):
        import search
        resp = search.handler(make_event(), {})
        for entry in json.loads(resp["body"])["results"]:
            assert "secret" not in entry
            assert "value" not in entry

    def test_post_method_returns_405(self):
        import search
        resp = search.handler(make_event(method="POST"), {})
        assert resp["statusCode"] == 405
