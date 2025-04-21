# Installation
.venv:
	poetry install --all-groups

install: .venv

# Linters
.isort:
	poetry run isort

.black:
	poetry run black .

.pylint:
	poetry run pylint --jobs 4

.mypy:
	poetry run mypy

.flake8:
	poetry run flake8


.lint: .isort .black .flake8 .mypy .pylint
lint: .venv .lint