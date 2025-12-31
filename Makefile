.PHONY: help build install test clean

help: ## Show help for available commands
	@echo Available commands:
	@echo   build            - Build project (install dependencies and package)
	@echo   install          - Install project dependencies
	@echo   test   			 - Run tests from tests/acceptance
	@echo   clean            - Clean temporary files and cache
	@echo   help             - Show this help message

install: ## Install project dependencies
	# TODO

build: install ## Build project (install dependencies and package)

test: ## Run acceptance tests from tests/acceptance
	@echo Running acceptance tests...
	behave tests/acceptance

clean: ## Clean temporary files and cache
	@echo Cleaning temporary files...
	# TODO
	@echo Cleaning completed

