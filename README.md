
# Deprecated Project

This project is now deprecated. The functionality has been reimplemented using
[Yeoman](https://yeoman.io/) and [PDM](https://pdm.fming.dev/).

The [stackstate-lab](https://github.com/stackstate-lab/generator-stackstate-lab) Yeoman generator can be used to 
scaffold new StackState Agent Check projects using a basic check structure or a more complex structure that uses
the [StackState ETL Framework](https://github.com/stackstate-etl/).

The generated project uses [PDM](https://pdm.fming.dev/) for Python package and dependency management which 
supports the latest PEP standards. Especially [PEP 582 support](https://www.python.org/dev/peps/pep-0582), no virtualenv involved at all.
[PDM Scripts](https://pdm.fming.dev/latest/usage/scripts/) was another compeling feature that aided the migration
of `stsdev` functionality.

| Command        | Description                                                                                                                |
|----------------|----------------------------------------------------------------------------------------------------------------------------|
| pdm install    | Installs package and setups up PEP 582 environment                                                                         |
| pdm test       | Runs unit tests                                                                                                            |
| pdm format     | Code styling and linting performed by Black, FlakeHell and MyPy                                                            |
| pdm build      | Will transpile the custom agent check to Python 2.7 and create install zip                                                 |
| pdm cleanAgent | Remove the custom StackState Agent Docker image used during development                                                    |
| pdm buildAgent | Build a custom [StackState Agent Docker](https://hub.docker.com/r/stackstate/stackstate-agent-2) to use during development |
| pdm check      | Dry-run custom agent check inside the StackState Agent container                                                           |
| pdm serve      | Starts the StackState Agent in the foreground using the configuration `src/data/conf.d/` directory                         |


---
# ~~StsDev - Development for StackState Agent Integrations~~

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
poetry run typer stslab_dev.cli.main utils docs --name stsdev --output ./docs/Documentation.md   


```


## Installation

Prerequisites:
- python 3.7+
- [Poetry](https://python-poetry.org/docs/#installation)
- [Docker](https://www.docker.com/get-started)


Using `pip` to install `stsdev`.

```bash
python -m pip install https://github.com/stackstate-lab/stslab-dev/releases/download/v0.0.7/stslab_dev-0.0.7-py3-none-any.whl

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
Install all dependencies for scaffolded project
```console
$ stsdev update  
```

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

### Build the project
To build the project,
```console
$ stsdev build  
```
This will automatically run code formatting, linting, tests and finally the build.

### Packaging checks


```console
$ stsdev package
```
This will automatically run code formatting, linting, tests and finally the packaging.
A zip file is created in the `dist` directory.  Copy this to the host running the agent and unzip it.
Run the `install.sh`. 


## Usage

See [stsdev documentation](./docs/Documentation.md)