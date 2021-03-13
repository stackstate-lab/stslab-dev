import importlib.resources as pkg_resources
import os
import shutil
from os import path
from string import Template

import requests
import typer

from . import templates


class Project(object):
    def __init__(
        self, proj_name, integration_name, echo=typer.echo, checkbase_version="1.8.1"
    ):
        self.echo = echo
        self.proj_name = proj_name
        self.integration_name = integration_name
        self.integration_src_dir = path.join(
            self.proj_name, "src", self.integration_name
        )
        self.integration_tests_dir = path.join(self.proj_name, "tests")
        self.integration_resources_dir = path.join(
            self.integration_tests_dir, "resources"
        )
        self.integration_confd_dir = path.join(self.integration_resources_dir, "conf.d")
        self.checksbase_dir = path.join(self.proj_name, ".ststemp")
        self.checksbase_dep_path = path.join(
            ".ststemp", "packages", "stackstate_checks_base"
        )
        self.checksbase_version = checkbase_version
        self.sts_url = f"https://github.com/StackVista/stackstate-agent-integrations/archive/{checkbase_version}.tar.gz"

    def run(self):
        if path.exists(self.proj_name):
            self.echo(f"Project {self.proj_name} already exists!")
            return 1
        os.makedirs(self.checksbase_dir)
        os.makedirs(self.integration_src_dir)
        os.makedirs(self.integration_tests_dir)
        os.makedirs(self.integration_confd_dir)
        self._popuplate_scaffold_files()
        return self._download_checksbase_packages()

    def _popuplate_scaffold_files(self):
        self._copy_template_to(
            "README.md.tpl", self.proj_name, {"project_name": self.proj_name}
        )
        self._copy_template_to(
            "pyproject.toml.tpl",
            self.proj_name,
            {
                "project_name": self.proj_name,
                "package_name": self.integration_name,
                "checksbase_path": self.checksbase_dep_path,
            },
        )
        self._copy_template_to("stackstate.yaml.tpl", self.integration_resources_dir)
        self._copy_template_to(".gitignore.tpl", self.proj_name)
        self._copy_template_to("mypy.ini.tpl", self.proj_name)
        self._write_file(path.join(self.integration_src_dir, "__init__.py"), "")

        env_entries = [
            "STS_URL=http://localhost:7070",
            "STS_API_KEY=xxxx",
            "# Define additional docker run commands to include in agent image",
            "#STSDEV_IMAGE_EXT=path/to/file/with/docker/run/commands"
        ]
        self._write_file(path.join(self.proj_name, ".env"), "\n".join(env_entries))

    def _copy_template_to(self, src_template, base_dir, placeholders=None):
        if placeholders is None:
            placeholders = {}
        target = (
            src_template if not src_template.endswith(".tpl") else src_template[0:-4]
        )
        target_path = path.join(base_dir, target)
        t = Template(pkg_resources.read_text(templates, src_template))
        self._write_file(target_path, t.substitute(**placeholders))

    @staticmethod
    def _write_file(target, content):
        with open(target, "w") as f:
            f.write(content)

    def _download_checksbase_packages(self):
        target_tar_gz = path.join(self.checksbase_dir, "sts-integrations.tar.gz")
        response = requests.get(self.sts_url, stream=True)
        if response.status_code == 200:
            with open(target_tar_gz, "wb") as f:
                f.write(response.raw.read())
        else:
            self.echo(
                f"Failed to download '{self.sts_url}', response code '{response.status_code}'",
                err=True,
            )
            self.echo(response.text, err=True)
            return 1
        shutil.unpack_archive(
            filename=target_tar_gz, extract_dir=self.checksbase_dir, format="gztar"
        )
        os.rename(
            path.join(
                self.checksbase_dir,
                f"stackstate-agent-integrations-{self.checksbase_version}",
            ),
            path.join(self.checksbase_dir, "packages"),
        )
        return 0
