from stslab_dev.cli.commands.agent import Agent


def test_docker_image_does_not_exists():
    agent = Agent(image="xxxxx")
    assert not agent.image_exists()


def test_build_dev_image():
    agent = Agent(image="stackstate/stackstate-agent-2-test-build:latest")
    agent.build_image()
    assert agent.image_exists()
    agent.delete_image()
    assert not agent.image_exists()
