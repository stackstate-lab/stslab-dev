import importlib.resources as pkg_resources
import os
from os import path
from string import Template

import typer

from . import templates


class Project(object):
    def __init__(self, proj_name, integration_name, echo=typer.echo, version="1.10.1"):
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
        self.version = version
        self.integration_confd_dir = path.join(self.integration_resources_dir, "conf.d")

    def run(self):
        if path.exists(self.proj_name):
            self.echo(f"Project {self.proj_name} already exists!")
            return 1
        os.makedirs(self.integration_src_dir)
        os.makedirs(self.integration_tests_dir)
        os.makedirs(self.integration_confd_dir)
        self._popuplate_scaffold_files()
        return 0

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
                "version": self.version,
            },
        )
        self._copy_template_to("stackstate.yaml.tpl", self.integration_resources_dir)
        self._copy_template_to(".gitignore.tpl", self.proj_name)
        self._copy_template_to("mypy.ini.tpl", self.proj_name)

        self._write_file(path.join(self.integration_src_dir, "__init__.py"), "")

        env_entries = [
            "STS_URL=http://localhost:7070",
            "STS_API_KEY=xxxx",
            "CURL_CA_BUNDLE=",
            "# Define additional docker run commands to include in agent image",
            "#STSDEV_IMAGE_EXT=path/to/file/with/docker/run/commands",
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
