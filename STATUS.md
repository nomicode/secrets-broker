# STATUS

Last updated: 2026-03-12

## Current state

5 open PRs split from original monolith branch. All pushed, all have open PRs on GitHub.

| PR | Branch | Status |
|----|--------|--------|
| #1 | claude/chore/tooling-setup | open, ready for review |
| #2 | claude/chore/ci-config | open, ready for review |
| #3 | claude/chore/trunk-config | open, @nomi-bot tasked with Makefile integration |
| #4 | claude/feat/broker-core | open, ready for review |
| #5 | claude/feat/broker-registry | open, ready for review |

feature/netlify-broker -- original monolith, superseded by above 5.

## Netlify

- Site: secrets-broker.netlify.app
- Site ID: c0a738d1-066b-4e98-9756-5d48b9de68ee
- PAT: nfp_7QAKXgLhGk9kdr7fyenDpxG3S89HZ1ve0082
- Env vars configured: CLAUDE_ACCESS_TOKEN, GITHUB_ACCESS_TOKEN, HUGGINGFACE_ACCESS_TOKEN, SLACK_APP_ACCESS_TOKEN, WAVESPEED_API_KEY
- Netlify Identity: not yet configured (needed before first deploy)

## Tests

65/65 passing. Covers: registry, request, poll, details, submit, search.

## Trunk

18 linters enabled: actionlint, bandit, black, checkov, codespell, git-diff-check, isort, markdownlint, osv-scanner, prettier, pyright, ruff, semgrep, shellcheck, shfmt, taplo, trufflehog, yamllint.

Git hooks not yet installed. CI workflow not yet created.

## Blockers

None. All work is unblocked and ready for review/merge.

## Next session priorities

1. Merge PRs (or have @nomi-bot do it)
2. Finish trunk integration on PR #3
3. Update submit.py for env-var-based secret reading (no user typing)
4. Deploy to Netlify and test end-to-end
5. Create jiffy repo (nomicode/jiffy)
