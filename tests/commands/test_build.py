import os
import shutil
from os.path import join

from py.path import local as localpath

from stslab_dev.cli.commands.build import BuildWorkspace


def prep_project_dir(tmpdir: localpath) -> localpath:
    sample_project_dir = join(os.getcwd(), "tests", "resources", "sample_project")
    project_dir = tmpdir.join("myproject")
    shutil.copytree(sample_project_dir, project_dir)
    return project_dir


def test_prepare_workspace(tmpdir: localpath) -> None:
    # tmpdir = localpath(join(os.getcwd(), "build"))
    project_dir = prep_project_dir(tmpdir)

    with (project_dir.as_cwd()):
        agent_dir = project_dir.join(".agent")
        bw = BuildWorkspace(str(project_dir))
        bw.prepare_workspace()
        assert agent_dir.exists()
        assert agent_dir.join("stackstate.yaml").exists()
        assert agent_dir.join("requirements.txt").exists()
        assert agent_dir.join("conf.d", "acmecheck.d", "conf.yaml").exists()
        assert agent_dir.join("conf.d", "acmecheck.d", "conf.yaml.example").exists()


def test_package_workspace(tmpdir: localpath) -> None:
    # tmpdir = localpath(join(os.getcwd(), "build"))
    project_dir = prep_project_dir(tmpdir)

    with (project_dir.as_cwd()):
        agent_dir = project_dir.join(".agent")
        dist_dir = project_dir.join("dist")
        bw = BuildWorkspace(str(project_dir))
        bw.package_workspace()
        assert agent_dir.exists()
        assert agent_dir.join("stackstate.yaml").exists() is False
        assert agent_dir.join("requirements.txt").exists()
        assert agent_dir.join("conf.d", "acmecheck.d", "conf.yaml").exists() is False
        assert agent_dir.join("conf.d", "acmecheck.d", "conf.yaml.example").exists()
        assert dist_dir.join("sts_acme_checks-0.1.0.zip").exists()
