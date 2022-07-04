MODULE_NAME := jobsity_challenge
POETRY := $(shell command -v poetry 2> /dev/null)
.DEFAULT_GOAL = help

.PHONY: help
help:
	@echo "Options:"
	@echo "--------"
	@echo "help: show this message"
	@echo "test: run pytest"
	@echo "clean: clean ./dist folder"
	@echo "build: test, clean and generate a wheel file in ./dist"

.PHONY: test
test:
	$(POETRY) run pytest

.PHONY: clean
clean:
	rm -fr ./dist

.PHONY: lint
lint:
	$(POETRY) run black --check ./tests/ $(MODULE_NAME) --diff
	$(POETRY) run flake8 ./tests/ $(MODULE_NAME)
	$(POETRY) run mypy $(MODULE_NAME)
	$(POETRY) run pylint ./tests/ $(MODULE_NAME)
	$(POETRY) run isort --check-only ./tests/ $(MODULE_NAME) --diff

.PHONY: format
format:
	$(POETRY) run black ./tests/ $(MODULE_NAME)
	$(POETRY) run isort ./tests/ $(MODULE_NAME)

.PHONY: build
build:
	docker-compose up --build
