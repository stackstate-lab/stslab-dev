import typer

from .commands.project import Project

app = typer.Typer(help="Help manage integration project")


@app.command("new")
def project(
    name: str = typer.Option(..., help="Name of project."),
    package: str = typer.Option(..., help="Package to store sources in."),
    version: str = typer.Option(
        "1.10.1", help="`stackstate_checks` version. This is a git tag."
    ),
):
    """Scaffold a new project for developing StackState Agent integrations
    examples:
      stsdev create-project sts-myfirst-integration sts_my_first_checks
    """
    typer.echo(f"Creating project {name}")
    rc = Project(name, package, version).run()
    if rc == 0:
        typer.echo("Created successfully. Remember to update .env with your settings.")
        typer.echo("Happy developing!")
