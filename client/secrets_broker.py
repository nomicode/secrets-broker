"""
secrets_broker - client for the human-in-the-loop secret broker.

Usage:
    from client.secrets_broker import request_secret
    value = request_secret("AWS_ACCESS_KEY")

Environment variables:
    SECRETS_BROKER_URL          broker base URL
                                (default: https://secrets-broker.netlify.app)
    SECRETS_BROKER_CALLBACK_URL optional URL the broker POSTs the secret to
                                on approval (alternative to polling)
"""
import json
import os
import platform
import subprocess
import sys
import time
import urllib.error
import urllib.request
from typing import Optional

BROKER_URL = os.environ.get(
    "SECRETS_BROKER_URL", "https://secrets-broker.netlify.app"
).rstrip("/")

_POLL_INTERVAL = 2   # seconds between polls
_DEFAULT_TIMEOUT = 300  # 5 minutes


def request_secret(
    label: str,
    callback_url: Optional[str] = None,
    timeout: int = _DEFAULT_TIMEOUT,
) -> str:
    """
    Request a secret from the broker.

    Opens the approval form in the local browser, then polls until the
    user approves or denies (or timeout is reached).

    Returns the secret string on approval.
    Raises PermissionError if denied.
    Raises TimeoutError if not responded to within `timeout` seconds.
    """
    callback_url = callback_url or os.environ.get("SECRETS_BROKER_CALLBACK_URL", "")

    result = _post("/api/request", {"label": label, "callback_url": callback_url})
    token = result["token"]
    form_url = result["form_url"]

    print(f"[secrets-broker] requesting : {label}", file=sys.stderr)
    print(f"[secrets-broker] approve at : {form_url}", file=sys.stderr)
    _open_browser(form_url)

    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        time.sleep(_POLL_INTERVAL)
        status, body = _get(f"/api/poll?token={token}")
        if status == 200:
            return body["secret"]
        if status == 403:
            raise PermissionError(f"secret request denied: {label!r}")
        if status == 404:
            raise LookupError(f"secret request expired: {label!r}")
        # 202 = still pending, keep polling

    raise TimeoutError(f"timed out waiting for secret approval: {label!r}")


# ---------------------------------------------------------------------------
# internals
# ---------------------------------------------------------------------------

def _post(path: str, data: dict) -> dict:
    req = urllib.request.Request(
        f"{BROKER_URL}{path}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def _get(path: str) -> tuple[int, dict]:
    try:
        with urllib.request.urlopen(f"{BROKER_URL}{path}", timeout=10) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
        except Exception:
            body = {}
        return e.code, body


def _open_browser(url: str) -> None:
    system = platform.system()
    try:
        if system == "Darwin":
            subprocess.Popen(["open", url])
        elif system == "Linux":
            subprocess.Popen(["xdg-open", url])
        elif system == "Windows":
            subprocess.Popen(["start", url], shell=True)
    except Exception:
        pass  # best-effort; URL is also printed to stderr


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def search_secrets(name: str = "", scope: str = "") -> list[dict]:
    """
    Search the secret catalog.

    Args:
        name:  OR-separated terms, e.g. "hf or huggingface"
        scope: glob pattern, e.g. "ml.*" or "workflow.*"

    Returns list of matching catalog entries.
    """
    params = []
    if name:
        params.append(f"name={urllib.request.quote(name)}")
    if scope:
        params.append(f"scope={urllib.request.quote(scope)}")
    qs = "?" + "&".join(params) if params else ""
    _, body = _get(f"/api/search{qs}")
    return body.get("results", [])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("usage: python secrets_broker.py <label>", file=sys.stderr)
        sys.exit(1)
    print(request_secret(sys.argv[1]))
