import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import blobs


def handler(event, context):
    if event["httpMethod"] != "GET":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    token = (event.get("queryStringParameters") or {}).get("token", "").strip()
    if not token:
        return _json(400, {"error": "token required"})

    record = blobs.get(token)
    if not record:
        return _json(404, {"error": "not found or expired"})

    status = record["status"]

    if status == "pending":
        return _json(202, {"status": "pending"})

    if status == "denied":
        blobs.delete(token)
        return _json(403, {"status": "denied"})

    # approved - return secret and burn the token
    secret = record.get("secret", "")
    blobs.delete(token)
    return _json(200, {"status": "approved", "secret": secret})


def _json(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data),
    }
