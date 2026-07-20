# =============================================================================
# Project configuration
# =============================================================================
PROJECT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME := sqlalchemy-state-machine
SRC_PATH := src/sqlalchemy_state_machine
LINT_PATHS := src tests examples
UV ?= uv

.DEFAULT_GOAL := help

.PHONY: help venv/install/main venv/install/all lint/ruff lint/mypy lint format clean test build sys/changelog sys/tag

# =============================================================================
# Help
# =============================================================================
help: ## Display this help message
	@awk 'BEGIN { FS = ":.*##"; printf "\nUsage:\n  make <target>\n\nTargets:\n" } /^[a-zA-Z0-9_./-]+:.*##/ { printf "  \033[36m%-24s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# =============================================================================
# Environment
# =============================================================================
venv/install/main: ## Install main dependencies
	@echo "==> Installing $(PROJECT_NAME) main dependencies"
	$(UV) sync --no-group dev

venv/install/all: ## Install all dependency groups
	@echo "==> Installing $(PROJECT_NAME) with all dependency groups"
	$(UV) sync --all-groups

# =============================================================================
# Code quality
# =============================================================================
lint/ruff: ## Check formatting and lint with Ruff
	@echo "==> Checking formatting and linting with Ruff"
	$(UV) run --locked ruff format --check $(LINT_PATHS)
	$(UV) run --locked ruff check $(LINT_PATHS)

lint/mypy: ## Type-check the source package with mypy
	@echo "==> Type-checking $(SRC_PATH) with mypy"
	$(UV) run --locked mypy $(SRC_PATH)

lint: lint/ruff lint/mypy ## Run all lint checks
	@echo "==> Lint checks passed"

format: ## Format and auto-fix lint issues
	@echo "==> Formatting and auto-fixing lint issues"
	$(UV) run --locked ruff format $(LINT_PATHS)
	$(UV) run --locked ruff check --fix $(LINT_PATHS)

# =============================================================================
# Test and build
# =============================================================================
test: ## Run the test suite with coverage
	@echo "==> Testing $(PROJECT_NAME) with coverage"
	$(UV) run --locked pytest --cov=sqlalchemy_state_machine --cov-report=term-missing

build: ## Build distribution packages
	@echo "==> Building $(PROJECT_NAME) distribution packages"
	$(UV) build

clean: ## Remove generated files and caches
	@echo "==> Removing generated files and caches"
	rm -rf .coverage .mypy_cache .pytest_cache .ruff_cache build dist
	find . -type d -name __pycache__ -prune -exec rm -rf {} +

# =============================================================================
# Release automation
# =============================================================================
# Requires mktemp, available on the project's supported macOS and Linux development environments.
sys/changelog: ## Generate CHANGELOG.md from historical version tags
	@echo "==> Generating CHANGELOG.md from version tags"
	@tmp_file=$$(mktemp CHANGELOG.md.XXXXXX) || exit $$?; \
	cleanup() { rm -f "$$tmp_file"; }; \
	trap cleanup 0; \
	trap 'exit 1' HUP INT TERM; \
	tags="$$( $(UV) run --locked python -c 'import re, subprocess, sys; pattern = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$$"); raw = subprocess.check_output(["git", "tag"], text=True).splitlines(); tagged = [(tuple(map(int, match.groups())), tag) for tag in raw if (match := pattern.fullmatch(tag))]; len({version for version, _ in tagged}) == len(tagged) or sys.exit("duplicate semantic-version tags are not supported"); tagged.sort(reverse=True); print(" ".join(tag for _, tag in tagged))' )" || exit $$?; \
	if [ -z "$$tags" ]; then \
		echo "No semantic-version tags found." >&2; \
		exit 1; \
	fi; \
	{ \
		printf '# Changelog\n\n'; \
		set -- $$tags; \
		newest_tag=$$1; \
		unreleased=$$(git log --no-merges "$$newest_tag..HEAD" --format='* %s [%an]' --reverse) || exit $$?; \
		if [ -n "$$unreleased" ]; then \
			printf '## Unreleased\n\n%s\n\n' "$$unreleased"; \
		fi; \
		while [ $$# -gt 0 ]; do \
			current_tag=$$1; \
			shift; \
			older_tag=$${1:-}; \
			tag_date=$$(git log -1 --format=%as "$$current_tag") || exit $$?; \
			display_tag=$${current_tag#v}; \
			printf '## %s (%s)\n\n' "$$display_tag" "$$tag_date"; \
			if [ -n "$$older_tag" ]; then range="$$older_tag..$$current_tag"; else range="$$current_tag"; fi; \
			git log --no-merges "$$range" --format='* %s [%an]' --reverse || exit $$?; \
			printf '\n'; \
		done; \
	} > "$$tmp_file" || exit $$?; \
	if ! mv "$$tmp_file" CHANGELOG.md; then \
		echo "Unable to replace CHANGELOG.md." >&2; \
		exit 1; \
	fi; \
	trap - 0; \
	echo "CHANGELOG.md generated successfully."

sys/tag: ## Create and push a vX.Y.Z release tag
	@read -r -p "Enter tag version (e.g., 2.0.0): " TAG; \
	if ! printf '%s\n' "$$TAG" | grep -Eq '^[0-9]+\.[0-9]+\.[0-9]+$$'; then \
		echo "Tag version must use the X.Y.Z format (for example, 2.0.0)" >&2; \
		exit 1; \
	fi; \
	project_version="$$( $(UV) run --locked python -c 'import tomllib; print(tomllib.load(open("pyproject.toml", "rb"))["project"]["version"])' )" || exit $$?; \
	if [ "$$project_version" != "$$TAG" ]; then \
		echo "Tag version $$TAG does not match pyproject.toml project.version $$project_version" >&2; \
		exit 1; \
	fi; \
	if [ -n "$$(git status --porcelain --untracked-files=all)" ]; then \
		echo "Worktree must be clean before creating a release tag." >&2; \
		exit 1; \
	fi; \
	if git show-ref --verify --quiet "refs/tags/v$$TAG"; then \
		echo "Local tag v$$TAG already exists." >&2; \
		exit 1; \
	fi; \
	echo "==> Creating and pushing v$$TAG"; \
	git tag -a "v$$TAG" -m "Release v$$TAG" || exit $$?; \
	if ! git push origin "v$$TAG"; then \
		echo "Push failed; deleting local tag v$$TAG." >&2; \
		git tag -d "v$$TAG" || exit $$?; \
		exit 1; \
	fi
