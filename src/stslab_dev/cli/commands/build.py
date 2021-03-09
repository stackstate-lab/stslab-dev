import os
import pathlib
import re
import shutil
from os.path import join as j

import toml
import typer
from plumbum import local
from py_backwards import const, exceptions, messages
from py_backwards.compiler import compile_files


class BuildWorkspace:
    def __init__(self, base_dir: str, echo=typer.echo) -> None:
        self.echo = echo
        self.agent_dir = j(base_dir, ".agent")
        self.checks_d_dir = j(self.agent_dir, "checks.d")
        self.dist_dir = j(base_dir, "dist")
        self.conf_d_dir = j(self.agent_dir, "conf.d")
        self.test_dir = j(base_dir, "tests")
        self.resources_dir = j(self.test_dir, "resources")
        self.stackstate_yaml = j(self.resources_dir, "stackstate.yaml")
        self.test_conf_d_dir = j(self.resources_dir, "conf.d")
        self.test_share_dir = j(self.resources_dir, "share")
        self.src_dir = j(base_dir, "src")
        self.pkg_name = os.listdir(self.src_dir)[0]
        self.pkg_dir = j(self.src_dir, self.pkg_name)

    def prepare_workspace(self, package_build: bool = False) -> None:
        shutil.rmtree(self.agent_dir, ignore_errors=True)
        os.makedirs(self.checks_d_dir)
        if package_build:
            ignore_conf_yamls = shutil.ignore_patterns("conf.yaml")
            shutil.copytree(self.test_conf_d_dir, self.conf_d_dir, ignore=ignore_conf_yamls)
        else:
            shutil.copytree(self.test_conf_d_dir, self.conf_d_dir)
            if os.path.exists(self.test_share_dir):
                shutil.copytree(self.test_share_dir, self.agent_dir)
            if os.path.exists(self.stackstate_yaml):
                shutil.copy(self.stackstate_yaml, j(self.agent_dir, "stackstate.yaml"))

        self._compile_to_py27()
        self._setup_requirements_txt()

    def package_workspace(self) -> None:
        self.prepare_workspace(package_build=True)
        pyproject_data = toml.loads(pathlib.Path("pyproject.toml").read_text())
        project_version = pyproject_data["tool"]["poetry"]["version"]
        os.makedirs(self.dist_dir)
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
        self.echo(f"Packaging version {project_version} of {self.pkg_name}")
        with (open(j(self.agent_dir, "install.sh"), mode="w")) as f:
            f.write(install_file)
        zipfile = f"{self.pkg_name}-{project_version}"
        shutil.make_archive(j(self.dist_dir, zipfile), "zip", self.agent_dir)

    def _compile_to_py27(self) -> None:
        try:
            result = compile_files(
                self.pkg_dir, self.checks_d_dir, const.TARGETS["2.7"]
            )
            self.echo(messages.compilation_result(result))
        except exceptions.CompilationError as e:
            self.echo(messages.syntax_error(e), err=True)
            raise e
        except exceptions.TransformationError as e:
            self.echo(messages.transformation_error(e), err=True)
            raise e
        except PermissionError as e:
            self.echo(messages.permission_error(self.checks_d_dir), err=True)
            raise e

    def _setup_requirements_txt(self) -> None:
        poetry = local["poetry"]
        requirements = poetry["export", "--without-hashes"]()
        if requirements.strip() == "":
            return
        lines = []
        matcher = re.compile("^[A-Za-z0-9]*==")
        for line in requirements.splitlines():
            match = matcher.match(line)
            if match:
                lines.append(line.split(";")[0])
        requirements_file = f"{self.agent_dir}/requirements.txt"
        with (open(requirements_file, mode="w")) as f:
            f.write("\n".join(lines))
