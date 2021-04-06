import importlib.resources as pkg_resources
import os
from os import path
from string import Template

import typer
from dotenv import load_dotenv

from . import templates


class Checks(object):
    def __init__(self, check_name: str, echo=typer.echo):
        load_dotenv(dotenv_path=".env")
        dirs_in_src = [d for d in os.listdir("src") if not str(d).startswith(".")]
        self.integration_pkg = os.path.join("src", str(dirs_in_src[0]))
        self.check_name = check_name
        self.check_name_capitalize = check_name[0].upper() + check_name[1:]
        self.check_name_lower = check_name.lower()
        self.echo = echo
        self.integration_tests_dir = "tests"
        self.integration_resources_dir = path.join(
            self.integration_tests_dir, "resources"
        )
        self.integration_confd_dir = path.join(self.integration_resources_dir, "conf.d")

        self.check_src_file = path.join(
            self.integration_pkg, f"{self.check_name_lower}.py"
        )
        self.check_test_file = path.join(
            self.integration_tests_dir, f"test_{self.check_name_lower}.py"
        )
        self.check_confd_dir = path.join(
            self.integration_confd_dir, f"{self.check_name_lower}.d"
        )
        self.check_confd_file = path.join(self.check_confd_dir, "conf.yaml.example")
        self.check_pkg = (
            f"{self.integration_pkg.split(os.path.sep)[-1]}.{self.check_name_lower}"
        )

    def run(self):

        if path.exists(self.check_src_file):
            self.echo(
                f"Check {self.check_name} ({self.check_src_file}) already exists!"
            )
            return 1

        if not path.exists(self.check_confd_dir):
            os.makedirs(self.check_confd_dir)

        class_name = (
            self.check_name_capitalize
            if self.check_name_capitalize.endswith("heck")
            else f"{self.check_name_capitalize}Check"
        )

        self._copy_template_to(
            "check.py.tpl",
            self.check_src_file,
            {
                "class_name": class_name,
            },
        )

        self._copy_template_to(
            "test_check.py.tpl",
            self.check_test_file,
            {
                "class_name": class_name,
                "check_pkg": self.check_pkg,
                "check_name_lower": self.check_name_lower,
            },
        )

        self._copy_template_to(
            "conf.yaml.example.tpl",
            self.check_confd_file,
            {"check_name_lower": self.check_name_lower},
        )

        return 0

    def _copy_template_to(self, src_template, target_file, placeholders):
        t = Template(pkg_resources.read_text(templates, src_template))
        with open(target_file, "w") as f:
            f.write(t.substitute(**placeholders))
