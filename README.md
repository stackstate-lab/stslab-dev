# StsDev - Development for StackState Agent Integrations

StsDev helps you declare, build, test and package StackStage Agent Integration projects,
ensuring you have a consistent development experience.

## Development

Prerequisites:
- python 3.7+
- pyenv
- [Poetry](https://python-poetry.org/)

```bash
# Install dependencies
poetry install
# Code Formatting
poetry run black src tests
# Linting
poetry run flakehell lint
#Testing
poetry run pytest
#Build
poetry build
# Generate documentation
typer stslab_dev.cli.main utils docs --name stsdev --output ./docs/Documentation.md   


```


## Installation

Prerequisites:
- python 3.7+t
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/get-started)


Using `pip` to install `stsdev`.

**Note:** 
For now please manually download from release section and then use pip to install.
This is due to this repository currently being private.

```bash
python -m pip install https://github.com/stackstate-lab/stslab-dev/releases/download/v0.0.1/stslab_dev-0.0.1-py3-none-any.whl

```

## Quick-Start

`stsdev` is a tool to aid with the development StackState Agent integrations.

### Starting a new project

```bash
stsdev project new --name my-custom-acme-checks --package sts_acme_checks

```

This will scaffold a new project called *my-custom-acme-checks*.  The package name *sts_acme_checks* will
be created in `my-custom-acme-checks/src/` to hold the sources for custom checks.
Tests will be created in `my-custom-acme-checks/tests/`.

### Managing dependencies

[Poetry](https://python-poetry.org/) is used as the packaging and dependency management system.

Dependencies for your project can be managed through `poetry add` or `poetry add -D` for development dependency.

```console
$ poetry add PyYAML  
```

### Build the project
To build the project,
```console
$ stsdev build  
```
This will automatically run code formatting, linting, tests and finally the build.


### Creating check

```console
$ stsdev checks create AcmeCheck
```
Will scaffold a sample,
* check -  `my-custom-acme-checks/src/acmecheck.py`
* test -   `tests/test_acmecheck.py`
* configuration - `tests/resources/conf.d/acmecheck.d/conf.yaml.example`


The sample check and test shows the technique to create StackState components, relationships
from a custom check, how to unit them and how to configure them to run in the agent.

### Unit Testing
To run tests in the project,
```console
$ stsdev test 
```
This will automatically run code formatting, linting, and tests.

### Dry-run a check

A check can be dry-run inside the StackState Agent by running 
```console
$ sudo -u stackstate-agent check xxx
```
`stsdev` makes this take simple by packaging your checks and running the agent check using docker.

```console
$ stsdev agent check acmecheck
```
Before running the command, remember to copy the example conf `tests/resources/conf.d/acmecheck.d/conf.yaml.example` to
`tests/resources/conf.d/acmecheck.d/conf.yaml`.


### Running checks in the Agent

Starts the StackState Agent in the foreground using the test configuration `tests/resources/conf.d`

```console
$ stsdev agent run
```

### Packaging checks


```console
$ stsdev package
```
This will automatically run code formatting, linting, tests and finally the packaging.
A zip file is created in the `dist` directory.  Copy this to the host running the agent and unzip it.
Run the `install.sh`. 


## Usage

See [stsdev documentation](./docs/Documentation.md)