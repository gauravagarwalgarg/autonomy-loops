# AutonomyLoops Developer commands
# Works on both GitHub and GitLab hosted copies.

.PHONY: help install dev-setup test lint format typecheck build docs docs-serve clean run sync

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install package
	pip install -e .

dev-setup: ## Install with dev dependencies
	pip install -e ".[dev,all]"
	pip install mkdocs-material mkdocs-minify-plugin mkdocs-git-revision-date-localized-plugin

test: ## Run test suite
	pytest tests/ -v --cov=autonomy_loops --cov-report=term-missing

lint: ## Run linter
	ruff check autonomy_loops/ tests/

format: ## Format code
	ruff format autonomy_loops/ tests/

typecheck: ## Run type checker
	mypy autonomy_loops/

build: ## Build distribution package
	python -m build

docs: ## Build documentation (MkDocs Material)
	mkdocs build --strict

docs-serve: ## Serve docs locally with live reload
	mkdocs serve --dev-addr 0.0.0.0:8000

clean: ## Clean build artifacts
	rm -rf dist/ build/ site/ public/ *.egg-info .pytest_cache .mypy_cache .ruff_cache __pycache__
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

run: ## Run agent (usage: make run TASK="implement auth module")
	autonomy-loops run --task "$(TASK)"

orchestrate: ## Run pipeline (usage: make orchestrate PIPELINE=pipelines/ci-review.yaml)
	autonomy-loops orchestrate --pipeline "$(PIPELINE)"

serve: ## Start dashboard server
	autonomy-loops serve --port 8091

sync: ## Push to both GitHub and GitLab remotes
	bash scripts/sync-remotes.sh

docker-build: ## Build Docker image
	docker build -t autonomy-loops .

docker-up: ## Start full stack with Docker Compose
	docker-compose up -d

docker-down: ## Stop Docker Compose stack
	docker-compose down
