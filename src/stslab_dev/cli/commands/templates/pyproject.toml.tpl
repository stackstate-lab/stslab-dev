[tool.poetry]
name = "$package_name"
version = "0.1.0"
description = "$project_name Custom Checks"
authors = ["Your Name <your@email.address>"]

[tool.poetry.dependencies]
python = ">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, !=3.6.* <=4.0.0"
pyyaml = "^3.13"
schematics = "^2.1.0"

[tool.poetry.dev-dependencies]
pytest = "*"
tox = "^3.22.0"
# StackState Agent Integration dev deps
prometheus-client = "^0.3.0"
six = "^1.12.0"
Deprecated = "^1.2.11"
requests = "^2.24.0"
pytest-sugar = "^0.9.4"
colorama = "^0.4.4"

[tool.tox]
legacy_tox_ini = """
[tox]
requires =
    tox-py-backwards
isolated_build = true
envlist = py27
[testenv]
whitelist_externals = poetry
poetry_add_dev_dependencies = True
deps =
    -e git+https://github.com/StackVista/stackstate-agent-integrations.git@$version#egg=stackstate_checks_base&subdirectory=stackstate_checks_base
    pytest
    pytest-sugar
    prometheus-client
    six
    Deprecated
    requests
    enum34
py_backwards = true
commands =
    pip uninstall -y $package_name
    poetry install
    poetry run pytest -W ignore::DeprecationWarning
"""

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

[tool.flakehell]
exclude = ["README.rst", "README.md", ".eggs", ".tox", "build",".venv", ".agent"]
include = ["src", "tests"]
format = "colored"
max_line_length = 120
show_source = true
# Temp fix until issue is fixed https://github.com/flakehell/flakehell/issues/10
extended_default_ignore=[]

[tool.flakehell.plugins]
"*" = [
    "+*",
    "-E203",
    ]

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

