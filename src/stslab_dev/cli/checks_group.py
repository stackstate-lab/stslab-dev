import typer
from .commands.checks import Checks


app = typer.Typer(help="Help manage checks in a project")


@app.command("create")
def check(check_name: str):
    """Scaffold a new project for developing StackState Agent integrations
    examples:
      stsdev create-project sts-myfirst-integration sts_my_first_checks
    """
    typer.echo(f"Creating check {check_name}")
    rc = Checks(check_name).run()
    if rc == 0:
        typer.echo("Created successfully.")
