import typer
from . import agent_group, checks_group, project_group
from plumbum import local, FG
from plumbum.commands.processes import ProcessExecutionError


app = typer.Typer(help="CLI for the development of StackState Agent integrations")
app.add_typer(agent_group.app, name="agent")
app.add_typer(checks_group.app, name="checks")
app.add_typer(project_group.app, name="project")

poetry = local["poetry"]
poetry_run = poetry["run"]


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
            typer.echo("Formatting code...")
            poetry_run["black", "src", "tests"] & FG
            typer.echo("Checking code style...")
            poetry_run["flakehell", "lint"] & FG
            typer.echo("All done!")
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


def main():
    app()
