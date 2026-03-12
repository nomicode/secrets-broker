# Detect CI environment (set by GitHub Actions and most CI systems)
ifdef CI
TRUNK_FLAGS := --no-color --no-progress --ci
TRUNK_ALL   := --all
else
TRUNK_FLAGS :=
TRUNK_ALL   :=
endif

TRUNK := ./node_modules/.bin/trunk

.PHONY: help install fmt check test ci build release clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "%-12s %s\n", $$1, $$2}'

## Sentinel: ensure trunk is installed before any lint/fmt target
$(TRUNK):
	@echo "trunk not found at $(TRUNK). Run ./bootstrap.sh to install dependencies."
	@exit 1

install: ## Install all project dependencies (node + python)
	yarn install --frozen-lockfile
	uv sync --dev

fmt: $(TRUNK) ## Format files (changed only locally, all in CI)
	direnv exec . trunk fmt $(TRUNK_FLAGS) $(TRUNK_ALL)

check: $(TRUNK) ## Lint files (changed only locally, all in CI)
	direnv exec . trunk check $(TRUNK_FLAGS) $(TRUNK_ALL)

test: ## Run pytest suite
	uv run pytest

ci: fmt check test ## Run full CI pipeline (fmt -> check -> test)

build: ci ## Build (depends on ci passing)
	@echo "build: ok"

release: ci ## Release (depends on ci passing)
	@echo "release: ok"

clean: ## Remove build artefacts and caches
	git clean -fd .trunk/out .venv node_modules __pycache__ .pytest_cache 2>/dev/null || true
