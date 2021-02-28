import typer
import os
from plumbum import local, FG
from dotenv import load_dotenv


class Agent(object):
    STS_API_KEY = "STS_API_KEY"
    STS_URL = "STS_URL"

    def __init__(self):
        self.docker = local["docker"]
        load_dotenv(dotenv_path=".env")

    def run_agent(self):
        agent_dir = self.prepare_agent_dir()
        self.docker[
            "run",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            "-e",
            f"STS_API_KEY={os.getenv(self.STS_API_KEY)}",
            "-e",
            f"STS_STS_URL={os.getenv(self.STS_URL)}",
            "-e",
            "DOCKER_STS_AGENT=false",
            "stackstate/stackstate-agent-2:latest",
        ] & FG

    def run_agent_check(self, check_name):
        agent_dir = self.prepare_agent_dir()
        self.docker[
            "run",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            "stackstate/stackstate-agent-2-dev:latest",
            "agent",
            "check",
            check_name,
        ] & FG

    @staticmethod
    def prepare_agent_dir():
        cwd = os.getcwd()
        typer.echo("Executing from working dir: %s" % cwd)
        rm = local["rm"]
        cp = local["cp"]["-r"]
        mkdir = local["mkdir"]["-p"]
        agent_dir = os.path.join(cwd, ".agent")
        checks_d_dir = os.path.join(agent_dir, "checks.d")
        conf_d_dir = os.path.join(agent_dir, "conf.d")
        test_dir = os.path.join(cwd, "tests")
        resources_dir = os.path.join(test_dir, "resources")
        stackstate_yaml = os.path.join(resources_dir, "stackstate.yaml")
        test_conf_d_dir = os.path.join(resources_dir, "conf.d")
        test_share_dir = os.path.join(resources_dir, "share")
        src_dir = os.path.join(cwd, "src")
        pkg_name = local.cmd.ls[src_dir]().strip()
        pkg_dir = os.path.join(src_dir, pkg_name)
        if os.path.exists(agent_dir):
            rm["-rf", agent_dir]()
        mkdir[checks_d_dir]()
        mkdir[conf_d_dir]()
        cp["%s/." % pkg_dir, checks_d_dir]()
        if os.path.exists(test_conf_d_dir):
            cp["%s/." % test_conf_d_dir, conf_d_dir]()
        if os.path.exists(test_share_dir):
            cp[test_share_dir, agent_dir]()
        if os.path.exists(stackstate_yaml):
            cp[stackstate_yaml, agent_dir]()
        return agent_dir
