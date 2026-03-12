"""
GET /api/search?name=hf+or+huggingface&scope=ml.*

Search the secret catalog by name/alias (OR terms, substring) and/or
scope (fnmatch glob against the entry's scopes list).

Also served as GET /available-secrets (no params = return everything).
"""
import fnmatch
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import catalog


def handler(event, context):
    if event["httpMethod"] != "GET":
        return {"statusCode": 405, "body": "Method Not Allowed"}

    params = event.get("queryStringParameters") or {}
    raw_name = (params.get("name") or "").strip()
    raw_scope = (params.get("scope") or "").strip()

    entries = catalog.load()

    if raw_name:
        # split on " or " (case-insensitive) to get OR terms
        terms = [t.strip().lower() for t in raw_name.lower().split(" or ") if t.strip()]
        entries = [e for e in entries if _name_matches(e, terms)]

    if raw_scope:
        entries = [e for e in entries if _scope_matches(e, raw_scope)]

    return _json(200, {"results": entries, "total": len(entries)})


def _name_matches(entry: dict, terms: list[str]) -> bool:
    """True if any term is a substring of name or any alias."""
    haystack = [entry.get("name", "").lower()] + [
        a.lower() for a in entry.get("aliases", [])
    ]
    return any(term in h for term in terms for h in haystack)


def _scope_matches(entry: dict, pattern: str) -> bool:
    """True if any of the entry's scopes matches the glob pattern."""
    scopes = entry.get("scopes", [])
    return any(fnmatch.fnmatch(s, pattern) for s in scopes)


def _json(status: int, data: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
        "body": json.dumps(data),
    }
