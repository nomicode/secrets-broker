# DEVLOG

Design decisions and session notes, newest first.

---

## 2026-03-12 -- initial build session

### Research phase

Investigated options for secret management in ephemeral/agentic contexts:
- 1Password SDK: desktop integration with biometric approval, but local-only (IPC)
- 1Password community feature request for remote approval exists but not shipped
- Infisical: has approval workflows but requires Pro tier
- GitHub Actions deployment protection rules: viable for env secrets, not arbitrary values
- Zapier Human in the Loop: has Collect Data action but reviewer must be logged into Zapier
- Custom broker approach chosen: Netlify functions + Identity + Blobs

### Architecture decisions

- Netlify over AWS/GCP: zero infra, built-in Identity, Blobs for ephemeral state
- Static registry over dynamic catalog: secrets already in Netlify env vars, no need to type them
- Token burned on first read: single-use, prevents replay
- 5 min TTL on blobs: limits exposure window
- Netlify Identity gate on submit: prevents unauthorized approval even with leaked form URL

### Token introspection research

Available reflection APIs per service:
- GitHub: GET api.github.com, check X-OAuth-Scopes response header (classic PATs only)
- HuggingFace: GET huggingface.co/api/whoami-v2 returns permissions
- Slack: POST slack.com/api/auth.test returns workspace info
- Anthropic: no public introspection endpoint
- WaveSpeed: no introspection, 401 if invalid

### jiffy design

Companion project for binary distribution. GNU coreutils model:
one zip per platform, one install.sh entry point, mirrors upstream binaries.
GitHub Releases latest-download redirect pattern for stable URLs.
Install: curl -fsSL https://github.com/nomicode/jiffy/releases/latest/download/install.sh | sh

### PR split

Original work was on single feature/netlify-broker branch (violated atomic PR rule).
Split into 5 atomic PRs. Makefile examples searched across nomicode repos
(vidsqueeze, wip-lintfree, dip, .github) for patterns: sentinel targets,
trunk integration, help targets, CI detection.

### Makefile examples from nomicode repos

- vidsqueeze: `trunk := node_modules/.bin/trunk; $(trunk): yarn install`
- wip-lintfree: complex DAG, ANSI macros, 21 linter targets, obelist integration
- dip: clean sed/column help target, poetry workflow
- .github: `.DEFAULT_GOAL := lint`, `.trunk: yarn trunk init`
