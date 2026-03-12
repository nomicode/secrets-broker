"""
POST   /api/catalog         register or update a secret entry (Identity-gated)
DELETE /api/catalog?name=.. remove an entry (Identity-gated)

Entry shape:
  {
    "name":        "huggingface-token",       required, unique key
    "aliases":     ["hf", "huggingface"],     optional
    "scopes":      ["ml.training"],           optional
    "description": "HuggingFace API token"   optional
  }
"""
import json
import os
import sys

import requests as _r

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import catalog

SITE_URL = os.environ.get("URL", "https://secrets-broker.netlify.app").rstrip("/")


def handler(event, context):
    method = event["httpMethod"]

    auth = (event.get("headers") or {}).get("authorization", "")
    if not _verify_identity(auth):
        return _json(401, {"error": "unauthorized"})

    if method == "POST":
        return _handle_add(event)
    if method == "DELETE":
        return _handle_remove(event)
    return {"statusCode": 405, "body": "Method Not Allowed"}


def _handle_add(event) -> dict:
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _json(400, {"error": "invalid JSON"})

    name = (body.get("name") or "").strip()
    if not name:
        return _json(400, {"error": "name required"})

    entry = {
        "name": name,
        "aliases": [a.strip() for a in body.get("aliases", []) if a.strip()],
        "scopes": [s.strip() for s in body.get("scopes", []) if s.strip()],
        "description": (body.get("description") or "").strip(),
    }
    updated = catalog.add(entry)
    return _json(200, {"ok": True, "total": len(updated)})


def _handle_remove(event) -> dict:
    name = ((event.get("queryStringParameters") or {}).get("name") or "").strip()
    if not name:
        return _json(400, {"error": "name required"})

    found = catalog.remove(name)
    if not found:
        return _json(404, {"error": "not found"})
    return _json(200, {"ok": True})


def _verify_identity(auth_header: str) -> bool:
    if not auth_header or not auth_header.startswith("Bearer "):
        return False
    token = auth_header[7:]
    r = _r.get(
        f"{SITE_URL}/.netlify/identity/user",
        headers={"Authorization": f"Bearer {token}"},
        timeout=5,
    )
    return r.status_code == 200


def _json(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data),
    }
