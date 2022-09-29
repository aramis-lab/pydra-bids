.EXPORT_ALL_VARIABLES:

ifneq (,$(wildcard .env))
include .env
endif

POETRY ?= poetry
PACKAGES = pydra

all: install test

.PHONY: install
install:
	@$(POETRY) install

.PHONY: install-docs
install-docs:
	@$(POETRY) install --only docs

.PHONY: format
format: format-black format-isort

.PHONY: format-black
format-black:
	$(info Formatting code with black)
	@$(POETRY) run black --quiet $(PACKAGES)

.PHONY: format-isort
format-isort:
	$(info Formatting code with isort)
	@$(POETRY) run isort --quiet $(PACKAGES)

.PHONY: lint
lint: lint-black lint-isort

.PHONY: lint-black
lint-black:
	$(info Linting code with black)
	@$(POETRY) run black --check --diff $(PACKAGES)

.PHONY: lint-isort
lint-isort:
	$(info Linting code with isort)
	@$(POETRY) run isort --check --diff $(PACKAGES)

.PHONY: clean-docs
clean-docs:
	@$(POETRY) run make -C docs clean

.PHONY: docs
docs: clean-docs
	@$(POETRY) run make -C docs html

.PHONY: test
test:
	@$(POETRY) run python -m pytest

.PHONY: update
update:
	@$(POETRY) update

.PHONY: publish
publish: publish-pypi

.PHONY: publish-pypi
publish-pypi: clean dist
ifdef PYPI_API_TOKEN
	@$(POETRY) publish --build --username __token__ --password $(PYPI_API_TOKEN)
else
	$(error PyPI API token not provided.)
endif

.PHONY: publish-testpypi
publish-testpypi: config-testpypi clean dist
ifdef TESTPYPI_API_TOKEN
	@$(POETRY) publish --build --repository testpypi --username __token__ --password $(TESTPYPI_API_TOKEN)
else
	$(error TestPyPI API token not provided.)
endif

.PHONY: config-testpypi
config-testpypi:
	@$(POETRY) config repositories.testpypi https://test.pypi.org/legacy
