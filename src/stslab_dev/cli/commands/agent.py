import typer
import os
from plumbum import local, FG
from dotenv import load_dotenv
import pathlib
import toml


class Agent(object):
    STS_API_KEY = "STS_API_KEY"
    STS_URL = "STS_URL"

    def __init__(
        self, image="stackstate/stackstate-agent-2-dev:latest", echo=typer.echo
    ):
        self.echo = echo
        self.docker = local["docker"]
        self.poetry = local["poetry"]
        self.image = image
        load_dotenv(dotenv_path=".env")

    def prepare_to_run(self):
        agent_dir = self.prepare_agent_dir()
        self.build_image()
        self.setup_requirements_txt(agent_dir)
        return agent_dir

    def run_agent(self):
        agent_dir = self.prepare_to_run()
        self.docker[
            "run",
            "--rm",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            "-e",
            f"STS_API_KEY={os.getenv(self.STS_API_KEY)}",
            "-e",
            f"STS_STS_URL={os.getenv(self.STS_URL)}",
            "-e",
            "DOCKER_STS_AGENT=false",
            self.image,
        ] & FG

    def run_agent_check(self, check_name):
        agent_dir = self.prepare_to_run()
        self.build_image()
        self.setup_requirements_txt(agent_dir)
        self.docker[
            "run",
            "--rm",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            self.image,
            "/opt/stackstate-agent/bin/run-dev-check.sh",
            check_name,
        ] & FG

    @staticmethod
    def setup_requirements_txt(agent_dir):
        poetry = local["poetry"]
        requirements = poetry["export", "--without-hashes"]()
        if requirements.strip() == "":
            return
        lines = []
        for line in requirements.splitlines():
            lines.append(line.split(";")[0])
        requirements_file = f"{agent_dir}/requirements.txt"
        with (open(requirements_file, mode="w")) as f:
            f.write("\n".join(lines))

    def package_checks(self):
        agent_dir = self.prepare_agent_dir()
        self.setup_requirements_txt(agent_dir)
        pyproject_data = toml.loads(pathlib.Path("pyproject.toml").read_text())
        project_version = pyproject_data["tool"]["poetry"]["version"]
        cwd = os.getcwd()
        local["mkdir"]["-p", "dist"]()
        pkg_name = os.getenv("STSDEV_PKG").split("/")[1]
        install_file = """#!/bin/bash
            if test -f "./requirements.txt"; then
                echo "Installing requirement"
                sudo -u stackstate-agent /opt/stackstate-agent/embedded/bin/pip install -r ./requirements.txt
            fi
            echo "Copying config and checks to /etc/stackstate-agent"
            sudo -u stackstate-agent cp -r ./conf.d/* /etc/stackstate-agent/conf.d
            sudo -u stackstate-agent cp -r ./checks.d/* /etc/stackstate-agent/checks.d
            echo "Done".
        """
        try:
            self.echo(f"Packaging version {project_version} of {pkg_name}")
            os.chdir(".agent")
            zipfile = f"{pkg_name}-{project_version}.zip"
            local["find"][agent_dir, "-name", "conf.yaml", "-exec", "rm", "{}", ";"]()
            with (open("install.sh", mode="w")) as f:
                f.write(install_file)
            local["zip"][
                "-rv", zipfile, "requirements.txt", "conf.d", "checks.d", "install.sh"
            ]()
            local["mv"][zipfile, "../dist"]()
            self.echo("All done!")
        finally:
            os.chdir(cwd)

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

    def image_exists(self):
        listing: str = self.docker[
            "images",
            self.image,
            "--format",
            "{{json . }}",
        ]()
        return listing.strip() != ""

    def delete_image(self):
        self.docker["rmi", "--force", self.image] & FG

    def build_image(self):
        if self.image_exists():
            return

        init_file = """#!/bin/bash\\n\\
            if test -f "/etc/stackstate-agent/requirements.txt"; then\\n\\
                echo "Installing requirement"\\n\\
                /opt/stackstate-agent/embedded/bin/pip install -r /etc/stackstate-agent/requirements.txt\\n\\
            fi\\n\\
        """
        run_check = f"""{init_file}\\n\\
            agent check "$1"\\n\\
        """
        dockerfile = f"""FROM stackstate/stackstate-agent-2:latest
        RUN apt update && \\
            apt-get install -yq iputils-ping && \\
            /opt/stackstate-agent/embedded/bin/pip uninstall -y requests && \\
            /opt/stackstate-agent/embedded/bin/pip install requests && \\
            /opt/stackstate-agent/embedded/bin/pip install pydevd-pycharm~=203.7148.57
        RUN echo '{init_file}' >> /etc/cont-init.d/95-load-requirement.sh
        RUN echo '{run_check}' >> /opt/stackstate-agent/bin/run-dev-check.sh
        RUN chmod +x /opt/stackstate-agent/bin/run-dev-check.sh /etc/cont-init.d/95-load-requirement.sh
        """
        docker_build = self.docker["build", "-t", self.image, "-"]
        complete_docker_build = docker_build << dockerfile
        self.echo("Building StackState Agent for Development")
        self.echo(complete_docker_build())
