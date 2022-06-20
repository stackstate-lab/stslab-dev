import os
import pathlib
import re
import shutil
from os.path import join as j

import toml
import typer
from dotenv import load_dotenv
from plumbum import local
from py_backwards import const, exceptions, messages
from py_backwards.compiler import compile_files


class BuildWorkspace:
    def __init__(self, base_dir: str, echo=typer.echo) -> None:
        load_dotenv(dotenv_path=".env")
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
        dirs_in_src = [
            d for d in os.listdir(self.src_dir) if not str(d).startswith(".")
        ]
        self.pkg_name = str(dirs_in_src[0])
        self.pkg_dir = j(self.src_dir, self.pkg_name)

    def prepare_workspace(self, package_build: bool = False) -> None:
        shutil.rmtree(self.agent_dir, ignore_errors=True)
        os.makedirs(self.agent_dir)
        if package_build:
            ignore_conf_yamls = shutil.ignore_patterns("conf.yaml")
            shutil.copytree(
                self.test_conf_d_dir, self.conf_d_dir, ignore=ignore_conf_yamls
            )
        else:
            shutil.copytree(self.test_conf_d_dir, self.conf_d_dir)
            if os.path.exists(self.test_share_dir):
                shutil.copytree(self.test_share_dir, j(self.agent_dir, "share"))
            if os.path.exists(self.stackstate_yaml):
                shutil.copy(self.stackstate_yaml, j(self.agent_dir, "stackstate.yaml"))

        # Copy resources in python package
        ignore_py_files = shutil.ignore_patterns("*.py")
        shutil.copytree(
            self.pkg_dir, self.checks_d_dir, ignore=ignore_py_files
        )

        self._compile_to_py27()
        self._setup_requirements_txt()

    def package_workspace(self) -> None:
        self.prepare_workspace(package_build=True)
        pyproject_data = toml.loads(pathlib.Path("pyproject.toml").read_text())
        project_version = pyproject_data["tool"]["poetry"]["version"]
        if not os.path.exists(self.dist_dir):
            os.makedirs(self.dist_dir)
        install_file = """#!/bin/bash
if test -f "./requirements.txt"; then
    echo "Installing requirement"
    sudo -u stackstate-agent /opt/stackstate-agent/embedded/bin/pip --no-cache-dir install -r ./requirements.txt
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
        compile_to_27 = os.getenv("compile_to_27", "true")
        if compile_to_27 != "true":
            return
        try:
            self.echo(f"Compiling files in {self.pkg_dir}  to {self.checks_d_dir}")
            result = compile_files(
                self.pkg_dir, self.checks_d_dir, const.TARGETS["2.7"]
            )
            if result.files == 0:
                self.echo("No python files found to compile.")
                raise Exception("Stopping because no custom checks found to compile")
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
        exclude_libs = os.getenv("EXCLUDE_LIBS", "")
        if exclude_libs != "":
            exclude_libs_list = [lib.strip() for lib in exclude_libs.split(",")]
        else:
            exclude_libs_list = []
        poetry = local["poetry"]
        requirements = poetry["export", "--without-hashes"]()
        if requirements.strip() == "":
            return
        lines = []
        matcher = re.compile("^[\\-A-Za-z0-9]*==")
        typing_found = False
        for line in requirements.splitlines():
            match = matcher.match(line)
            if match:
                lib_name_and_version = line.split(";")[0]
                lib_name = lib_name_and_version.split("==")[0].strip()
                if lib_name not in exclude_libs_list:
                    lines.append(lib_name_and_version)
                if lib_name_and_version.startswith("typing"):
                    typing_found = True
        requirements_file = f"{self.agent_dir}/requirements.txt"
        if not typing_found:
            lines.append(
                "typing==3.7.4"
            )  # This is to support the dangling imports in 2.7 for now.
        with (open(requirements_file, mode="w")) as f:
            f.write("\n".join(lines))
