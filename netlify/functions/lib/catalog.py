"""
Catalog index helpers.
The catalog is a single JSON blob stored under key "index" in the
"secret-catalog" store. All reads and writes go through here.
"""
import base64
import json
import os

import requests as _r

_STORE = "secret-catalog"
_KEY = "index"


def _ctx() -> dict:
    raw = os.environ.get("NETLIFY_BLOBS_CONTEXT", "")
    if not raw:
        raise RuntimeError("NETLIFY_BLOBS_CONTEXT not available")
    padded = raw + "=" * (-len(raw) % 4)
    return json.loads(base64.b64decode(padded))


def _url() -> str:
    ctx = _ctx()
    return f"{ctx['edgeURL']}/{ctx['siteID']}/{_STORE}/{_KEY}"


def _auth() -> dict:
    return {"Authorization": f"Bearer {_ctx()['token']}"}


def load() -> list[dict]:
    """Return the full catalog as a list of entries."""
    r = _r.get(_url(), headers=_auth(), timeout=10)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    return r.json().get("entries", [])


def save(entries: list[dict]) -> None:
    _r.put(
        _url(),
        json={"entries": entries},
        headers=_auth(),
        timeout=10,
    ).raise_for_status()


def add(entry: dict) -> list[dict]:
    """Add or replace an entry (matched by name). Returns updated catalog."""
    entries = load()
    entries = [e for e in entries if e["name"] != entry["name"]]
    entries.append(entry)
    save(entries)
    return entries


def remove(name: str) -> bool:
    """Remove entry by name. Returns True if it existed."""
    entries = load()
    filtered = [e for e in entries if e["name"] != name]
    if len(filtered) == len(entries):
        return False
    save(filtered)
    return True
