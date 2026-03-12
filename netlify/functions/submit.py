import json
import os
import sys

import requests as _r

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import blobs

SITE_URL = os.environ.get("URL", "https://secrets-broker.netlify.app").rstrip("/")


def handler(event, context):
    if event["httpMethod"] != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    auth = (event.get("headers") or {}).get("authorization", "")
    if not _verify_identity(auth):
        return _json(401, {"error": "unauthorized"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _json(400, {"error": "invalid JSON"})

    token = (body.get("token") or "").strip()
    action = (body.get("action") or "").strip()
    secret = (body.get("secret") or "").strip()

    if not token or action not in ("approve", "deny"):
        return _json(400, {"error": "token and valid action required"})

    record = blobs.get(token)
    if not record:
        return _json(404, {"error": "not found or expired"})

    if record["status"] != "pending":
        return _json(409, {"error": "already resolved"})

    record["status"] = "approved" if action == "approve" else "denied"
    record["secret"] = secret if action == "approve" else None
    blobs.put(token, record)

    callback_url = record.get("callback_url", "")
    if callback_url and action == "approve":
        try:
            _r.post(
                callback_url,
                json={"token": token, "secret": secret},
                timeout=5,
            )
        except _r.RequestException:
            pass  # best-effort

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
