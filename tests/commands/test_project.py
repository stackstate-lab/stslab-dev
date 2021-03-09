from os import path
from unittest.mock import MagicMock

from stslab_dev.cli.commands.project import Project

project_name = "test_project"
checks_pkg = "my_checks"


def test_project_dir_exists(tmpdir):
    typer_echo = MagicMock()
    with (tmpdir.as_cwd()):
        tmpdir.mkdir(project_name)
        project = Project(project_name, checks_pkg, typer_echo)
        rc = project.run()
        assert 1 == rc
        typer_echo.assert_called_with("Project test_project already exists!")


def test_project_scaffold(tmpdir):
    with (tmpdir.as_cwd()):
        project = Project(project_name, checks_pkg)
        rc = project.run()
        assert 0 == rc
        assert path.exists(f"{project_name}/src/{checks_pkg}/__init__.py")
        assert path.exists(f"{project_name}/tests/resources/stackstate.yaml")
        assert path.exists(f"{project_name}/.gitignore")
        assert path.exists(f"{project_name}/.env")
        assert path.exists(f"{project_name}/tests/resources/conf.d")
        assert path.exists(f"{project_name}/README.md")
        assert path.exists(f"{project_name}/pyproject.toml")
        assert path.exists(f"{project_name}/.ststemp/packages/stackstate_checks_base")
