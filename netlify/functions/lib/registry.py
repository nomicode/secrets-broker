"""
Static registry mapping Netlify env var names to human-readable metadata.
Add a new entry here whenever a new secret is added to the Netlify project.

Schema per entry:
  name        str   human-readable label shown in the approval form
  org         str   the service / organisation that issued the key
  type        str   pat | api_key | app_token | oauth_token
  aliases     list  short names accepted in search and request_secret()
  scopes      list  dot-namespaced tags used for scope filtering
  description str   one-liner shown in the approval form
"""

REGISTRY: dict[str, dict] = {
    "CLAUDE_ACCESS_TOKEN": {
        "name": "Claude API Key",
        "org": "Anthropic",
        "type": "api_key",
        "aliases": ["claude", "anthropic", "claude-api"],
        "scopes": ["ai.*", "llm.*", "claude.*"],
        "description": "Anthropic Claude API key for LLM inference",
    },
    "GITHUB_ACCESS_TOKEN": {
        "name": "GitHub Personal Access Token",
        "org": "GitHub",
        "type": "pat",
        "aliases": ["github", "gh", "github-token"],
        "scopes": ["github.*", "vcs.*", "git.*"],
        "description": "GitHub PAT for API access and git operations",
    },
    "HUGGINGFACE_ACCESS_TOKEN": {
        "name": "HuggingFace Access Token",
        "org": "HuggingFace",
        "type": "api_key",
        "aliases": ["hf", "huggingface", "hf-token"],
        "scopes": ["ml.*", "ai.*", "huggingface.*"],
        "description": "HuggingFace Hub token for model access and inference",
    },
    "SLACK_APP_ACCESS_TOKEN": {
        "name": "Slack App Access Token",
        "org": "Slack",
        "type": "app_token",
        "aliases": ["slack", "slack-token", "slack-app"],
        "scopes": ["slack.*", "messaging.*"],
        "description": "Slack app token for workspace messaging and API access",
    },
    "WAVESPEED_API_KEY": {
        "name": "WaveSpeed API Key",
        "org": "WaveSpeed",
        "type": "api_key",
        "aliases": ["wavespeed", "ws", "wavespeed-key"],
        "scopes": ["video.*", "media.*", "wavespeed.*"],
        "description": "WaveSpeed API key for video generation and processing",
    },
}


def resolve(label: str) -> str | None:
    """
    Resolve a label to a canonical env var key.

    Accepts exact env var names ("GITHUB_ACCESS_TOKEN") or any alias
    ("gh", "github"). Returns None if no match.
    """
    label_lower = label.strip().lower()

    # exact match on env var name (case-insensitive)
    for key in REGISTRY:
        if key.lower() == label_lower:
            return key

    # alias match
    for key, meta in REGISTRY.items():
        if label_lower in [a.lower() for a in meta.get("aliases", [])]:
            return key

    return None


def metadata(key: str) -> dict | None:
    """Return registry entry for a canonical key, or None."""
    return REGISTRY.get(key)


def search(name_terms: list[str], scope_pattern: str = "") -> list[dict]:
    """
    Return registry entries matching name terms and/or scope glob.

    name_terms  - list of lowercase substrings, OR logic across name + aliases
    scope_pattern - fnmatch glob applied to the entry's scopes list
    """
    import fnmatch

    results = []
    for key, meta in REGISTRY.items():
        if name_terms:
            haystack = [meta["name"].lower(), key.lower()] + [
                a.lower() for a in meta.get("aliases", [])
            ]
            if not any(term in h for term in name_terms for h in haystack):
                continue

        if scope_pattern:
            if not any(fnmatch.fnmatch(s, scope_pattern) for s in meta.get("scopes", [])):
                continue

        results.append({"key": key, **meta})

    return results
