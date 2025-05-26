# Formatters
.isort_fmt:
	poetry run isort . --skip .venv

.black_fmt:
	poetry run black . --exclude '/\.venv/'

.fmt: .isort_fmt .black_fmt
fmt: .venv .fmt

# Linters
.isort_lint:
	poetry run isort --check . --skip .venv

.black_lint:
	poetry run black --check --diff . --exclude '/\.venv/'

.pylint:
	poetry run pylint $(shell find . -type f -name "*.py" -not -path "./.venv/*")

.mypy:
	poetry run mypy . --exclude '/\.venv/'

.flake8:
	poetry run flake8 . --exclude=.venv

.lint: .isort_lint .black_lint .flake8 .mypy .pylint
lint: .venv .lint
