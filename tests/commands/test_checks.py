from stslab_dev.cli.commands.checks import Checks
from unittest.mock import MagicMock
import os
from os import path
from dotenv import load_dotenv

project_name = "test_project"
checks_pkg = "my_checks"
check_name = "MyCheck"


def write_file(target, content):
    with (open(target, "w")) as f:
        f.write(content)


def test_check_exists(tmpdir):
    typer_echo = MagicMock()
    with (tmpdir.as_cwd()):
        write_file(".env", "STSDEV_PKG=src/my_checks\n")
        load_dotenv(dotenv_path=f"{os.getcwd()}/.env")
        checks_pkg_dir = f"{os.getcwd()}/src/my_checks"
        os.makedirs(checks_pkg_dir)
        write_file(f"{checks_pkg_dir}/mycheck.py", "some stuff")
        checks = Checks(check_name, typer_echo)
        rc = checks.run()
        assert 1 == rc
        typer_echo.assert_called_with(
            "Check MyCheck (src/my_checks/mycheck.py) already exists!"
        )

        checks = Checks("MyCoolCheck")
        rc = checks.run()
        assert 0 == rc

        assert path.exists("src/my_checks/mycoolcheck.py")
        assert path.exists("tests/test_mycoolcheck.py")
        assert path.exists("tests/resources/conf.d/mycoolcheck.d/conf.yaml.example")
