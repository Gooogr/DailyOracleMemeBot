# Installation
.venv:
	poetry install --all-groups

install: .venv

# Formatters
.isort_fmt:
	poetry run isort .

.black_fmt:
	poetry run black .

.fmt: .isort_fmt .black_fmt
fmt: .venv .fmt


# Linters
.isort_lint:
	poetry run isort --check .

.black_lint:
	poetry run black --check --diff .

.pylint:
	poetry run pylint --jobs 4

.mypy:
	poetry run mypy .

.flake8:
	poetry run flake8 .

.lint: .isort_lint .black_lint .flake8 .mypy .pylint
lint: .venv .lint