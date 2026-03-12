# secrets-broker plan

## done

- repo initialized
- broker functions: request, details, submit, poll
- approval form: public/approve/index.html with Netlify Identity gate
- static registry: 5 keys with aliases + scopes
- search endpoint: fuzzy name OR terms, fnmatch scope globs
- client lib: request_secret(), search_secrets(), auto-open browser, poll loop
- 65/65 tests passing
- split into 5 atomic PRs (#1-#5)
- Makefile stub on PR #3
- trunk init with 18 linters + semgrep + codespell
- linting config ported from nomicode/dotfiles-old
- dependabot + automerge workflow
- sysops skill at ~/.claude/skills/sysops/SKILL.md

## in progress

- PR reviews and merging (#1-#5)
- trunk integration delegated to @nomi-bot on PR #3

## todo

### immediate

- submit.py: read secret from os.environ[key] instead of user-typed value
- update approval form to remove secret input for registry-backed keys
- Makefile: research trunk CI flags, wire hooks, ensure make ci passes
- trunk GitHub Actions CI workflow
- client lib as its own PR
- token introspection: GitHub (X-OAuth-Scopes), HuggingFace (/api/whoami-v2), Slack (auth.test)

### remote notification (punted)

options: Ntfy, Pushover, email. Needs SECRETS_BROKER_NOTIFY_URL env var.

### github actions integration

repository_dispatch as alternative request channel.

### admin UI, rate limiting, configurable TTL

### companion project: jiffy (nomicode/jiffy)

GNU coreutils binary distro for stateless LLM sessions.
install: curl -fsSL https://github.com/nomicode/jiffy/releases/latest/download/install.sh | sh
v1 tools: direnv, uv, trunk, yarn, make
platforms: darwin-arm64, darwin-x86_64, linux-arm64, linux-x86_64
model: mirror upstream bins, verify SHA256, assemble platform zips
