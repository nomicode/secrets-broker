# secrets-broker

Human-in-the-loop secret approval broker. Ephemeral form pages on Netlify, Netlify Identity for auth, Python serverless functions for logic.

## Overview

A process (e.g. Claude in an ephemeral container) requests a secret by label. The broker creates a short-lived approval form URL. A human opens the form, authenticates via Netlify Identity, and approves or denies. If approved, the secret (read from Netlify env vars) is returned to the polling process. The token is burned on first read.

## Architecture

```
process calls POST /api/request { label: "hf" }
  <- { token, form_url, poll_url }

form_url opens in browser
  -> Netlify Identity login gate
  -> "Process is requesting: HuggingFace Access Token"
  -> [Approve] [Deny]

POST /api/submit { token, action: "approve" }
  -> reads os.environ["HUGGINGFACE_ACCESS_TOKEN"]
  -> stores in blob, fires callback_url if set

GET /api/poll?token=abc123
  <- 202 pending | 200 approved (token burned) | 403 denied | 404 expired
```

## Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| POST | /api/request | Create pending request, returns form_url + poll_url |
| GET | /api/details?token= | Fetch request metadata |
| POST | /api/submit | Approve/deny (Identity-gated, reads secret from env) |
| GET | /api/poll?token= | Poll for result (burns token on read) |
| GET | /api/search?name=&scope= | Search registry by name/alias/scope |
| GET | /available-secrets | Alias for /api/search with no filters |

## Registry

Static registry in `netlify/functions/lib/registry.py`:

- CLAUDE_ACCESS_TOKEN (aliases: claude, anthropic) -- scopes: ai.*, llm.*
- GITHUB_ACCESS_TOKEN (aliases: github, gh) -- scopes: github.*, vcs.*
- HUGGINGFACE_ACCESS_TOKEN (aliases: hf, huggingface) -- scopes: ml.*, ai.*
- SLACK_APP_ACCESS_TOKEN (aliases: slack) -- scopes: slack.*, messaging.*
- WAVESPEED_API_KEY (aliases: wavespeed, ws) -- scopes: video.*, media.*

Search: `name=hf or claude`, `scope=ml.*`, combined filters.

## Client

```python
from client.secrets_broker import request_secret, search_secrets
results = search_secrets(name="hf", scope="ml.*")
value = request_secret("hf", timeout=300)
```

CLI: `python client/secrets_broker.py <label>`

## Netlify

- Site: secrets-broker.netlify.app
- Site ID: c0a738d1-066b-4e98-9756-5d48b9de68ee
- Auth: Netlify Identity
- State: Netlify Blobs (5 min TTL, burned on read)

## Dev

```sh
./bootstrap.sh && direnv allow .
uv run pytest            # 65 tests
direnv exec . trunk check --all  # 18 linters
```

## PRs

- #1 claude/chore/tooling-setup -- bootstrap, uv, yarn, direnv, pytest
- #2 claude/chore/ci-config -- dependabot automerge, sourcery
- #3 claude/chore/trunk-config -- 18 linters, Makefile, nomi defaults
- #4 claude/feat/broker-core -- request/approve/poll functions + tests
- #5 claude/feat/broker-registry -- static registry, search, scope filtering
