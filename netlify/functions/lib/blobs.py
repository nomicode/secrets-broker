"""
Thin wrapper around the Netlify Blobs HTTP API.
NETLIFY_BLOBS_CONTEXT is auto-injected by Netlify at function runtime.
"""
import base64
import json
import os

import requests as _r

_STORE = "secret-requests"
_DEFAULT_TTL = 300  # seconds


def _ctx() -> dict:
    raw = os.environ.get("NETLIFY_BLOBS_CONTEXT", "")
    if not raw:
        raise RuntimeError("NETLIFY_BLOBS_CONTEXT not available")
    padded = raw + "=" * (-len(raw) % 4)
    return json.loads(base64.b64decode(padded))


def _url(key: str) -> str:
    ctx = _ctx()
    return f"{ctx['edgeURL']}/{ctx['siteID']}/{_STORE}/{key}"


def _auth() -> dict:
    return {"Authorization": f"Bearer {_ctx()['token']}"}


def put(key: str, data: dict, ttl: int = _DEFAULT_TTL) -> None:
    _r.put(
        _url(key),
        json=data,
        headers={**_auth(), "Cache-Control": f"max-age={ttl}"},
        timeout=10,
    ).raise_for_status()


def get(key: str) -> dict | None:
    r = _r.get(_url(key), headers=_auth(), timeout=10)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()


def delete(key: str) -> None:
    r = _r.delete(_url(key), headers=_auth(), timeout=10)
    if r.status_code not in (200, 404):
        r.raise_for_status()
