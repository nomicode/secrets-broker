"""
Shared fixtures and helpers for secrets-broker tests.

Adds netlify/functions to sys.path so handler modules are importable,
and provides in-memory blob/catalog fakes plus common event builders.
"""
import os
import sys

import pytest
from unittest.mock import MagicMock

# make netlify/functions (and its lib/ sub-package) importable
sys.path.insert(
    0,
    os.path.join(os.path.dirname(__file__), "..", "netlify", "functions"),
)


# ---------------------------------------------------------------------------
# event builder
# ---------------------------------------------------------------------------

def make_event(
    method: str = "GET",
    body: str | None = None,
    params: dict | None = None,
    headers: dict | None = None,
) -> dict:
    return {
        "httpMethod": method,
        "body": body,
        "queryStringParameters": params or {},
        "headers": headers or {},
    }


# ---------------------------------------------------------------------------
# in-memory blob store
# ---------------------------------------------------------------------------

class MemoryBlobs:
    """Drop-in replacement for lib.blobs backed by a plain dict."""

    def __init__(self):
        self._store: dict = {}

    def put(self, key: str, data: dict, ttl: int = 300) -> None:
        self._store[key] = data

    def get(self, key: str) -> dict | None:
        return self._store.get(key)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    # test helpers
    def set_raw(self, key: str, data: dict) -> None:
        self._store[key] = data

    def keys(self) -> list:
        return list(self._store.keys())


@pytest.fixture
def mem_blobs() -> MemoryBlobs:
    return MemoryBlobs()


# ---------------------------------------------------------------------------
# identity mock helpers
# ---------------------------------------------------------------------------

@pytest.fixture
def authed_event(request):
    """GET or POST event with a valid Bearer token in headers."""
    method = getattr(request, "param", "POST")
    return make_event(method=method, headers={"authorization": "Bearer valid-jwt"})


def identity_ok() -> MagicMock:
    m = MagicMock()
    m.status_code = 200
    return m


def identity_fail() -> MagicMock:
    m = MagicMock()
    m.status_code = 401
    return m
