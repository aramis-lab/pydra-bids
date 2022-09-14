POETRY ?= poetry
PACKAGES = pydra
CONDA ?= conda

.PHONY: env
env:
	@$(CONDA) create -y -p ./.venv poetry

.PHONY: install
install:
	@$(POETRY) install

.PHONY: install-dev
install-dev:
	@$(POETRY) install --only dev

.PHONY: install-docs
install-docs:
	@$(POETRY) install --only docs

.PHONY: install-test
install-test:
	@$(POETRY) install --with test

.PHONY: format
format: install-dev format-black format-isort

.PHONY: format-black
format-black:
	$(info Formatting code with black)
	@$(POETRY) run black --quiet $(PACKAGES)

.PHONY: format-isort
format-isort:
	$(info Formatting code with isort)
	@$(POETRY) run isort --quiet $(PACKAGES)

.PHONY: lint
lint: install-dev lint-black lint-isort

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
docs: install-docs clean-docs
	@$(POETRY) run make -C docs html

.PHONY: test
test: install-test
	@$(POETRY) run python -m pytest
