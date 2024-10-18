.PHONY: sys/changelog
## Generating changelog file
sys/changelog:
	@echo "Generating CHANGELOG.md..."
	@echo "" > CHANGELOG.md;
	@previous_tag=0; \
	for current_tag in $$(git tag --sort=-creatordate); do \
		if [ "$$previous_tag" != 0 ]; then \
			tag_date=$$(git log -1 --pretty=format:'%ad' --date=short $${previous_tag}); \
			printf "\n## $${previous_tag} ($${tag_date})\n\n" >> CHANGELOG.md; \
			git log $${current_tag}...$${previous_tag} --pretty=format:'*  %s [%an]' --reverse | grep -v Merge >> CHANGELOG.md; \
			printf "\n" >> CHANGELOG.md; \
		fi; \
		previous_tag=$${current_tag}; \
	done
	@echo "CHANGELOG.md generated successfully."

.PHONY: sys/tag
## Create and push tag
sys/tag:
	@read -p "Enter tag version (e.g., 1.0.0): " TAG; \
	if [[ $$TAG =~ ^[0-9]+\.[0-9]+\.[0-9]+$$ ]]; then \
		git tag -a $$TAG -m $$TAG; \
		git push origin $$TAG; \
		echo "Tag $$TAG created and pushed successfully."; \
	else \
		echo "Invalid tag format. Please use X.Y.Z (e.g., 1.0.0)"; \
		exit 1; \
	fi

.PHONY: venv/install
## Install dev and lint dependencies
venv/install:
	@echo "install virtual environment..."
	@exec python -m pip install --upgrade pip
	@exec pip install --no-cache-dir -e .
	@exec pip install --no-cache-dir -r requirements/linters.txt
	@exec pip install --no-cache-dir -r requirements/tests.txt
	@exec make dev/clean

.PHONY: dev/lint
## Running all linters
dev/lint:
	@echo "Run isort"
	@exec isort .
	@echo "Run black"
	@exec black sqlalchemy_state_machine tests
	@echo "Run flake"
	@exec flake8 sqlalchemy_state_machine tests
	@echo "Run bandit"
	@exec bandit -r sqlalchemy_state_machine/*
	@echo "Run mypy"
	@exec mypy sqlalchemy_state_machine
	@exec rm -rf .mypy_cache

.PHONY: dev/test
## Run all tests
dev/test:
	@echo "Run tests"
	PYTHONPATH=${PYTHONPATH} PYTHONASYNCIODEBUG=x py.test -svvv -rs --cov sqlalchemy_state_machine --cov-report term-missing -x
	@exec rm -rf .pytest_cache

.PHONY: dev/clean
## Clear temp files
dev/clean:
	@echo "Clear temp files"
	@rm -rf `find . -name __pycache__`
	@rm -rf `find . -type f -name '*.py[co]' `
	@rm -rf `find . -type f -name '*~' `
	@rm -rf `find . -type f -name '.*~' `
	@rm -rf `find . -type f -name '@*' `
	@rm -rf `find . -type f -name '#*#' `
	@rm -rf `find . -type f -name '*.orig' `
	@rm -rf `find . -type f -name '*.rej' `
	@rm -rf .coverage
	@rm -rf coverage.html
	@rm -rf coverage.xml
	@rm -rf htmlcov
	@rm -rf build
	@rm -rf cover
	@python setup.py clean
	@rm -rf .develop
	@rm -rf .flake
	@rm -rf .install-deps
	@rm -rf *.egg-info
	@rm -rf .pytest_cache
	@rm -rf dist

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
