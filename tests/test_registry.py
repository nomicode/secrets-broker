"""Tests for lib/registry.py"""
import pytest
from lib import registry


class TestResolve:
    def test_exact_key_name(self):
        assert registry.resolve("GITHUB_ACCESS_TOKEN") == "GITHUB_ACCESS_TOKEN"

    def test_exact_key_case_insensitive(self):
        assert registry.resolve("github_access_token") == "GITHUB_ACCESS_TOKEN"

    def test_alias_gh(self):
        assert registry.resolve("gh") == "GITHUB_ACCESS_TOKEN"

    def test_alias_hf(self):
        assert registry.resolve("hf") == "HUGGINGFACE_ACCESS_TOKEN"

    def test_alias_huggingface(self):
        assert registry.resolve("huggingface") == "HUGGINGFACE_ACCESS_TOKEN"

    def test_alias_claude(self):
        assert registry.resolve("claude") == "CLAUDE_ACCESS_TOKEN"

    def test_alias_slack(self):
        assert registry.resolve("slack") == "SLACK_APP_ACCESS_TOKEN"

    def test_alias_wavespeed(self):
        assert registry.resolve("wavespeed") == "WAVESPEED_API_KEY"

    def test_unknown_label_returns_none(self):
        assert registry.resolve("totally-unknown-key") is None

    def test_empty_string_returns_none(self):
        assert registry.resolve("") is None


class TestMetadata:
    def test_known_key_returns_dict(self):
        meta = registry.metadata("GITHUB_ACCESS_TOKEN")
        assert meta is not None
        assert meta["org"] == "GitHub"
        assert meta["type"] == "pat"

    def test_unknown_key_returns_none(self):
        assert registry.metadata("DOES_NOT_EXIST") is None

    def test_all_entries_have_required_fields(self):
        required = {"name", "org", "type", "aliases", "scopes", "description"}
        for key, meta in registry.REGISTRY.items():
            missing = required - set(meta.keys())
            assert not missing, f"{key} missing fields: {missing}"


class TestSearch:
    def test_no_filters_returns_all(self):
        results = registry.search([])
        assert len(results) == len(registry.REGISTRY)

    def test_name_term_hf(self):
        results = registry.search(["hf"])
        keys = [r["key"] for r in results]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys

    def test_name_term_matches_alias(self):
        results = registry.search(["gh"])
        keys = [r["key"] for r in results]
        assert "GITHUB_ACCESS_TOKEN" in keys

    def test_name_or_logic(self):
        results = registry.search(["hf", "claude"])
        keys = [r["key"] for r in results]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys
        assert "CLAUDE_ACCESS_TOKEN" in keys

    def test_scope_glob_ml(self):
        results = registry.search([], scope_pattern="ml.*")
        keys = [r["key"] for r in results]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys
        assert "GITHUB_ACCESS_TOKEN" not in keys

    def test_scope_glob_ai_matches_multiple(self):
        results = registry.search([], scope_pattern="ai.*")
        keys = [r["key"] for r in results]
        assert "CLAUDE_ACCESS_TOKEN" in keys
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys

    def test_name_and_scope_combined(self):
        results = registry.search(["hf"], scope_pattern="ml.*")
        keys = [r["key"] for r in results]
        assert "HUGGINGFACE_ACCESS_TOKEN" in keys

    def test_name_and_scope_no_match(self):
        results = registry.search(["slack"], scope_pattern="ml.*")
        assert results == []

    def test_result_includes_key_field(self):
        results = registry.search(["github"])
        assert all("key" in r for r in results)

    def test_no_results_on_garbage_term(self):
        assert registry.search(["xyzzy-no-match"]) == []
