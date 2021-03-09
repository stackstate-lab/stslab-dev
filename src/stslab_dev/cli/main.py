
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



@app.command("apply-style")
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
    ignore_formatting: bool = typer.Option(
        "False", help="Ignore code formatting before running tests"
    ),
    use_tox: bool = typer.Option("True", help="Will use tox to run tests."),
):
    """Run tests for current project"""
    try:
        if not ignore_formatting:
            apply_style()
        typer.echo("Running tests ...")
        if use_tox:
            poetry_run["tox"] & FG
        else:
            poetry_run["pytest", "-v"] & FG
        return 0
    except ProcessExecutionError as e:
        return e.retcode


@app.command("build")
def build(use_tox: bool = typer.Option("True", help="Will use tox to run tests.")):
    """Build current project"""
    rc = test(ignore_formatting=False, use_tox=use_tox)
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
    run_tests: bool = typer.Option("True", help="Runs formatting, linting and tests"),
):
    """Build current project"""
    rc = 0
    if run_tests:
        rc = test(ignore_formatting=False, use_tox=use_tox)
    if rc == 0:
        BuildWorkspace(os.getcwd()).package_workspace()
    else:
        typer.echo("Stopping packaging.")


def main():
    app()
