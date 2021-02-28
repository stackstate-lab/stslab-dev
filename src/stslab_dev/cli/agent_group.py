import typer
from .commands.agent import Agent
from plumbum.commands.processes import ProcessExecutionError


app = typer.Typer(help="Help manage StackState Agent")


@app.command("run")
def run_agent():
    """Starts the StackState Agent in the foreground."""
    try:
        return Agent().run_agent()
    except ProcessExecutionError as e:
        return e.retcode


@app.command("check")
def check_agent(check_name):
    """Execute the check using the StackState Agent."""
    try:
        return Agent().run_agent_check(check_name)
    except ProcessExecutionError as e:
        return e.retcode
