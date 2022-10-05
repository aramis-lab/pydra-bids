POETRY ?= poetry
PACKAGES = pydra
INSTALL_STAMP = .install.stamp

ifneq (,$(wildcard .env))
include .env
endif

.EXPORT_ALL_VARIABLES:

all: clean install check test

.PHONY: check
check: check-black check-isort

.PHONY: check-black
check-black: $(INSTALL_STAMP)
	$(info Checking code with black)
	@$(POETRY) run black --check --diff $(PACKAGES)

.PHONY: check-isort
check-isort: $(INSTALL_STAMP)
	$(info Checking code with isort)
	@$(POETRY) run isort --check --diff $(PACKAGES)

.PHONY: clean
clean:
	$(RM) -r dist
	$(RM) -f $(INSTALL_STAMP)

.PHONY: clean-docs
clean-docs:
	@$(POETRY) run make -C docs clean

.PHONY: config-testpypi
config-testpypi:
	@$(POETRY) config repositories.testpypi https://test.pypi.org/legacy

.PHONY: docs
docs: $(INSTALL_STAMP) clean-docs
	@$(POETRY) run make -C docs html

.PHONY: format
format: format-black format-isort

.PHONY: format-black
format-black: $(INSTALL_STAMP)
	$(info Formatting code with black)
	@$(POETRY) run black --quiet $(PACKAGES)

.PHONY: format-isort
format-isort: $(INSTALL_STAMP)
	$(info Formatting code with isort)
	@$(POETRY) run isort --quiet $(PACKAGES)

.PHONY: install
install: $(INSTALL_STAMP)
$(INSTALL_STAMP): poetry.lock pyproject.toml
	@$(POETRY) install
	@touch $(INSTALL_STAMP)

.PHONY: publish
publish: publish-pypi

.PHONY: publish-pypi
publish-pypi:
ifdef PYPI_API_TOKEN
	@$(POETRY) publish --build --username __token__ --password $(PYPI_API_TOKEN)
else
	$(error PyPI API token not provided)
endif

.PHONY: publish-testpypi
publish-testpypi: config-testpypi
ifdef TESTPYPI_API_TOKEN
	@$(POETRY) publish --build --username __token__ --password $(TESTPYPI_API_TOKEN) --repository testpypi
else
	$(error TestPyPI API token not provided)
endif

.PHONY: test
test: $(INSTALL_STAMP)
	@$(POETRY) run python -m pytest

.PHONY: update
update: pyproject.toml
	@$(POETRY) update
