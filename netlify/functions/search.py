"""
GET /api/search?name=hf+or+huggingface&scope=ml.*

Search the static secret registry by name/alias (OR terms, substring)
and/or scope (fnmatch glob). Also served as GET /available-secrets.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import registry


def handler(event, context):
    if event["httpMethod"] != "GET":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    params = event.get("queryStringParameters") or {}
    raw_name = (params.get("name") or "").strip()
    raw_scope = (params.get("scope") or "").strip()

    terms = [t.strip().lower() for t in raw_name.lower().split(" or ") if t.strip()] if raw_name else []
    results = registry.search(terms, scope_pattern=raw_scope)

    return _json(200, {"results": results, "total": len(results)})


def _json(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data),
    }
