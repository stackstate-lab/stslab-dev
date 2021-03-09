[tool.poetry]
name = "$package_name"
version = "0.1.0"
description = "$project_name Custom Checks"
authors = ["Your Name <your@email.address>"]

[tool.poetry.dependencies]
python = "^3.7"

[tool.poetry.dev-dependencies]
pytest = "^5.2"
flakehell = "^0.9.0"
tox = "^3.22.0"
black = "^20.8b1"
py-backwards = "^0.7"
tox-py-backwards = "^0.1"
stackstate-checks-base = { path = "$checksbase_path", develop = false }
# StackState Agent Integration dev deps
pyyaml = "^3.13"
prometheus-client = "^0.3.0"
six = "^1.12.0"
schematics = "^2.1.0"
Deprecated = "^1.2.11"
requests = "^2.24.0"

[tool.black]
line-length = 120
target-version = ['py27']
include = '\.pyi?$$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.tox]
legacy_tox_ini = """
[tox]
isolated_build = true
envlist = python2
[testenv]
whitelist_externals = poetry
py_backwards = true
commands =
    poetry install -vvv
    poetry run pytest
"""

[tool.flakehell]
exclude = ["README.rst", "README.md", ".eggs", ".tox", "build",".venv", ".ststemp", ".agent"]
include = ["src", "tests"]
format = "colored"
max_line_length = 120
show_source = true

[tool.flakehell.plugins]
"*" = [
    "+*",
    "-E203",
    ]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

