.PHONY: tag
tag:
	@echo "Create tag"
	@git checkout master; 
	@git pull origin master; 
	@git fetch;
	@git tag -a  $(name) -m "$(name)"; 
	@git push origin $(name);
	@git push origin master

.PHONY: lint
lint:
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

.PHONY: test
test:
	@echo "Run tests"
	PYTHONPATH=${PYTHONPATH} PYTHONASYNCIODEBUG=x py.test -svvv -rs --cov sqlalchemy_state_machine --cov-report term-missing -x
	@exec rm -rf .pytest_cache

.PHONY: clean
clean:
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

.PHONY: help
help:
	@echo -n "Common make targets"
	@echo ":"
	@cat Makefile | sed -n '/^\.PHONY: / h; /\(^\t@*echo\|^\t:\)/ {H; x; /PHONY/ s/.PHONY: \(.*\)\n.*"\(.*\)"/  make \1\t\2/p; d; x}'| sort -k2,2 |expand -t 20
