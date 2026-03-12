import json
import os
import sys
import uuid
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import blobs

SITE_URL = os.environ.get("URL", "https://secrets-broker.netlify.app").rstrip("/")
TTL = 300


def handler(event, context):
    if event["httpMethod"] != "POST":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _json(400, {"error": "invalid JSON"})

    label = (body.get("label") or "").strip()
    if not label:
        return _json(400, {"error": "label required"})

    callback_url = (body.get("callback_url") or "").strip()
    token = uuid.uuid4().hex

    blobs.put(
        token,
        {
            "label": label,
            "callback_url": callback_url,
            "status": "pending",
            "secret": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
        ttl=TTL,
    )

    return _json(
        200,
        {
            "token": token,
            "form_url": f"{SITE_URL}/approve/?token={token}",
            "poll_url": f"{SITE_URL}/api/poll?token={token}",
        },
    )


def _json(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data),
    }
