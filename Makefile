POETRY := $(shell command -v poetry 2> /dev/null)
PYMODULE := concourse_dnf
INSTALL_STAMP := .install.stamp
TESTS = tests


all: install format lint test

install: $(INSTALL_STAMP)
$(INSTALL_STAMP): pyproject.toml
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run poetry install
	touch $(INSTALL_STAMP)

.PHONY: lint
lint: $(INSTALL_STAMP)
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run flake8
	$(POETRY) run black --check --diff --color $(PYMODULE) $(TESTS)
	$(POETRY) run isort --check-only $(PYMODULE) $(TESTS)

.PHONY: format
format: $(INSTALL_STAMP)
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run isort $(PYMODULE) $(TESTS)
	$(POETRY) run black $(PYMODULE) $(TESTS)

.PHONY: test
test: $(INSTALL_STAMP)
	@if [ -z $(POETRY) ]; then echo "Poetry could not be found. See https://python-poetry.org/docs/"; exit 2; fi
	$(POETRY) run tox
 
