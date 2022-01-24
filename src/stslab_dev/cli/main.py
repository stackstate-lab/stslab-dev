import os

import typer
from plumbum import FG, local
from plumbum.commands.processes import ProcessExecutionError

from . import agent_group, checks_group, project_group
from .commands.build import BuildWorkspace

app = typer.Typer(help="CLI for the development of StackState Agent integrations")
app.add_typer(agent_group.app, name="agent")
app.add_typer(checks_group.app, name="checks")
app.add_typer(project_group.app, name="project")

poetry = local["poetry"]
poetry_run = poetry["run"]


@app.command("code-style")
def apply_style():
    """Formats code using Black and check stype using Flake"""
    try:
        typer.echo("Formatting code...")
        poetry_run["black", "src", "tests"] & FG
        typer.echo("Sorting imports...")
        poetry_run["isort", "src"] & FG
        typer.echo("Checking code style...")
        poetry_run["flakehell", "lint"] & FG
        typer.echo("Checking typing...")
        poetry_run["mypy", "src"] & FG
        typer.echo("All done!")
        return 0
    except ProcessExecutionError as e:
        return e.retcode


@app.command("test")
def test(
    use_tox: bool = typer.Option("True", help="Will use tox to run tests."),
):
    """Run tests for current project"""
    try:
        typer.echo("Running tests ...")
        if use_tox:
            poetry_run["tox"] & FG
        else:
            poetry_run["pytest", "-v"] & FG
        return 0
    except ProcessExecutionError as e:
        return e.retcode


@app.command("build")
def build(
    use_tox: bool = typer.Option("True", help="Will use tox to run tests."),
    run_tests: bool = typer.Option("True", help="Runs tests"),
    code_style: bool = typer.Option("True", help="Apply code styling"),
):
    """Build current project"""
    rc = 0
    if code_style:
        rc = apply_style()
    if rc == 0 and run_tests:
        rc = test(use_tox=use_tox)
    if rc == 0:
        try:
            poetry["build"] & FG
        except ProcessExecutionError as e:
            return e.retcode
    else:
        typer.echo("Stopping build.")


@app.command("package")
def package(
    use_tox: bool = typer.Option("True", help="Will use tox to run tests."),
    run_tests: bool = typer.Option("True", help="Runs tests"),
    code_style: bool = typer.Option("True", help="Apply code styling"),
):
    """Build current project"""
    rc = 0
    if code_style:
        rc = apply_style()
    if rc == 0 and run_tests:
        rc = test(use_tox=use_tox)
    if rc == 0:
        BuildWorkspace(os.getcwd()).package_workspace()
    else:
        typer.echo("Stopping packaging.")


@app.command("update")
def update(
    version: str = typer.Option(
        "1.16.1", help="`stackstate_checks` version. This is a git tag."
    ),
    skip_poetry_install: bool = typer.Option("False", help="Skip poetry install"),
):
    """Installs the projects dependencies. Same a `poetry update` `poetry install` except it installs the
    `stackstate_checks` package from github. This is a temporary workaround until
    https://github.com/python-poetry/poetry/issues/755 is fixed.
    """

    url = (
        f"git+https://github.com/StackVista/stackstate-agent-integrations.git@{version}"
        f"#egg=stackstate_checks_base&subdirectory=stackstate_checks_base"
    )
    try:
        if not skip_poetry_install:
            poetry["update"] & FG
            poetry["install"] & FG

        poetry_run["pip", "install", "-e", url] & FG
        typer.echo("All done!")
    except ProcessExecutionError as e:
        return e.retcode


def main():
    app()
