# `stsdev`

CLI for the development of StackState Agent integrations

**Usage**:

```console
$ stsdev [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--install-completion`: Install completion for the current shell.
* `--show-completion`: Show completion for the current shell, to copy it or customize the installation.
* `--help`: Show this message and exit.

**Commands**:

* `agent`: Help manage StackState Agent
* `build`: Build current project
* `checks`: Help manage checks in a project
* `code-style`: Formats code using Black and check stype...
* `install`: Installs the projects dependencies.
* `package`: Build current project
* `project`: Help manage integration project
* `test`: Run tests for current project

## `stsdev agent`

Help manage StackState Agent

**Usage**:

```console
$ stsdev agent [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `check`: Execute the check using the StackState Agent.
* `clean`: Removes the development docker image for the...
* `run`: Starts the StackState Agent in the...

### `stsdev agent check`

Execute the check using the StackState Agent.

**Usage**:

```console
$ stsdev agent check [OPTIONS] CHECK_NAME
```

**Arguments**:

* `CHECK_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

### `stsdev agent clean`

Removes the development docker image for the StackState Agent.
Will be automatically build when needed.

**Usage**:

```console
$ stsdev agent clean [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

### `stsdev agent run`

Starts the StackState Agent in the foreground.

**Usage**:

```console
$ stsdev agent run [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `stsdev build`

Build current project

**Usage**:

```console
$ stsdev build [OPTIONS]
```

**Options**:

* `--use-tox / --no-use-tox`: Will use tox to run tests.  [default: True]
* `--run-tests / --no-run-tests`: Runs tests  [default: True]
* `--code-style / --no-code-style`: Apply code styling  [default: True]
* `--help`: Show this message and exit.

## `stsdev checks`

Help manage checks in a project

**Usage**:

```console
$ stsdev checks [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `create`: Scaffold a new project for developing...

### `stsdev checks create`

Scaffold a new project for developing StackState Agent integrations
examples:
  stsdev create-project sts-myfirst-integration sts_my_first_checks

**Usage**:

```console
$ stsdev checks create [OPTIONS] CHECK_NAME
```

**Arguments**:

* `CHECK_NAME`: [required]

**Options**:

* `--help`: Show this message and exit.

## `stsdev code-style`

Formats code using Black and check stype using Flake

**Usage**:

```console
$ stsdev code-style [OPTIONS]
```

**Options**:

* `--help`: Show this message and exit.

## `stsdev install`

Installs the projects dependencies. Same a `poetry install` except it installs the `stackstate_checks` package
from github. This is a temporary workaround until https://github.com/python-poetry/poetry/issues/755 is fixed.

**Usage**:

```console
$ stsdev install [OPTIONS]
```

**Options**:

* `--version TEXT`: `stackstate_checks` version. This is a git tag.  [default: 1.10.1]
* `--skip-poetry-install / --no-skip-poetry-install`: Skip poetry install  [default: False]
* `--help`: Show this message and exit.

## `stsdev package`

Build current project

**Usage**:

```console
$ stsdev package [OPTIONS]
```

**Options**:

* `--use-tox / --no-use-tox`: Will use tox to run tests.  [default: True]
* `--run-tests / --no-run-tests`: Runs tests  [default: True]
* `--code-style / --no-code-style`: Apply code styling  [default: True]
* `--help`: Show this message and exit.

## `stsdev project`

Help manage integration project

**Usage**:

```console
$ stsdev project [OPTIONS] COMMAND [ARGS]...
```

**Options**:

* `--help`: Show this message and exit.

**Commands**:

* `new`: Scaffold a new project for developing...

### `stsdev project new`

Scaffold a new project for developing StackState Agent integrations
examples:
  stsdev create-project sts-myfirst-integration sts_my_first_checks

**Usage**:

```console
$ stsdev project new [OPTIONS]
```

**Options**:

* `--name TEXT`: Name of project.  [required]
* `--package TEXT`: Package to store sources in.  [required]
* `--help`: Show this message and exit.

## `stsdev test`

Run tests for current project

**Usage**:

```console
$ stsdev test [OPTIONS]
```

**Options**:

* `--use-tox / --no-use-tox`: Will use tox to run tests.  [default: True]
* `--help`: Show this message and exit.
