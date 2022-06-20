import os

import typer
from dotenv import load_dotenv
from plumbum import FG, local

from .build import BuildWorkspace


class Agent:
    STS_API_KEY = "STS_API_KEY"
    STS_URL = "STS_URL"

    def __init__(
        self, image: str = "stackstate/stackstate-agent-2-dev:latest", echo=typer.echo
    ):
        self.echo = echo
        self.docker = local["docker"]
        self.poetry = local["poetry"]
        self.image = image
        load_dotenv(dotenv_path=".env")
        self.workspace = BuildWorkspace(os.getcwd())

    def prepare_to_run(self) -> str:
        self.workspace.prepare_workspace()
        self.build_image()
        return self.workspace.agent_dir

    def run_agent(self) -> None:
        agent_dir = self.prepare_to_run()
        self.docker[
            "run",
            "--rm",
            "-it",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            "-e",
            f"STS_API_KEY={os.getenv(self.STS_API_KEY)}",
            "-e",
            f"STS_STS_URL={os.getenv(self.STS_URL)}",
            "-e",
            "DOCKER_STS_AGENT=false",
            "-e",
            f"CURL_CA_BUNDLE={os.getenv('CURL_CA_BUNDLE', '')}",
            self.image,
            "/opt/stackstate-agent/bin/run-agent.sh"
        ] & FG

    def run_agent_check(self, check_name: str) -> None:
        agent_dir = self.prepare_to_run()
        self.docker[
            "run",
            "--rm",
            "-v",
            "%s:/etc/stackstate-agent" % agent_dir,
            "-e",
            f"CURL_CA_BUNDLE={os.getenv('CURL_CA_BUNDLE', '')}",
            self.image,
            "/opt/stackstate-agent/bin/run-dev-check.sh",
            check_name,
        ] & FG

    def image_exists(self) -> bool:
        listing: str = self.docker[
            "images",
            self.image,
            "--format",
            "{{json . }}",
        ]()
        return listing.strip() != ""

    def delete_image(self) -> None:
        self.docker["rmi", "--force", self.image] & FG

    def build_image(self, image="stackstate/stackstate-agent-2:latest", ) -> None:
        if self.image_exists():
            return
        commands = os.getenv("STSDEV_ADDITIONAL_COMMANDS", None)
        init_file = """#!/bin/bash\\n\\
            if test -f "/etc/stackstate-agent/requirements.txt"; then\\n\\
                echo "Installing requirement"\\n\\
                /opt/stackstate-agent/embedded/bin/pip install -r /etc/stackstate-agent/requirements.txt\\n\\
            fi\\n\\
        """
        run_check = f"{init_file}"
        run_agent = "#!/bin/bash\\n\\"
        if commands is not None:
            run_check = f"""{run_check}\\n\\
                echo "Running command {commands}"\\n\\ 
                nohup {commands} &\\n\\
            """
            run_agent = f"""{run_check}\\n\\
                echo "Running command {commands}"\\n\\ 
                nohup {commands} &\\n\\
            """

        run_check = f"""{run_check}
            agent check "$1"\\n\\
        """

        run_agent = f"""{run_agent}
            agent run\\n\\
        """
        dockerfile = f"""FROM '{image}'
        RUN apt update && \\
            apt-get install -yq iputils-ping libkrb5-3 gcc g++ && \\
            /opt/stackstate-agent/embedded/bin/pip uninstall -y requests && \\
            /opt/stackstate-agent/embedded/bin/pip install requests && \\
            /opt/stackstate-agent/embedded/bin/pip install pydevd-pycharm~=203.7148.57
        RUN echo '{init_file}' >> /etc/cont-init.d/95-load-requirement.sh
        RUN echo '{run_check}' >> /opt/stackstate-agent/bin/run-dev-check.sh
        RUN echo '{run_agent}' >> /opt/stackstate-agent/bin/run-agent.sh
        RUN chmod +x /opt/stackstate-agent/bin/run-agent.sh 
        RUN chmod +x /opt/stackstate-agent/bin/run-dev-check.sh /etc/cont-init.d/95-load-requirement.sh
        """
        docker_ext_file = os.getenv("STSDEV_IMAGE_EXT")
        if docker_ext_file:
            with open(docker_ext_file, "r") as f:
                dockerfile += f.read()

        self.echo("Building StackState Agent for Development:")
        self.echo(dockerfile)
        docker_build = self.docker["build", "-t", self.image, "-"]
        complete_docker_build = docker_build << dockerfile
        self.echo(complete_docker_build())
