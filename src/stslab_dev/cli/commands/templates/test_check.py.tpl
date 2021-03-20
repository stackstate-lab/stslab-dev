from $check_pkg import $class_name
from stackstate_checks.stubs import topology
import yaml


def assert_component(components: List[dict], cid: str) -> dict:
    component = next(iter(filter(lambda item: (item["id"] == cid), components)), None)
    assert component is not None
    return component


def assert_relation(relations: List[dict], sid: str, tid: str) -> dict:
    relation = next(
        iter(
            filter(
                # fmt: off
                lambda item: item["source_id"] == sid and item["target_id"] == tid,
                # fmt: on
                relations,
            )
        ),
        None,
    )
    assert relation is not None
    return relation


def test_$check_name_lower():
    topology.reset()
    instances = yaml.safe_load(instance_yaml)["instances"]

    check = $class_name("$check_name_lower", {}, {}, instances=instance)
    check.check(instances[0])
    snapshot = topology.get_snapshot("")
    components = snapshot["components"]
    relations = snapshot["relations"]
    app_id = "urn:$check_name_lower:/INTERNETBANKING"
    host_id = "urn:host:/SRV001"
    assert len(components) == 2
    assert_component(components, app_id)
    assert_component(components, host_id)
    assert len(relations) == 1
    assert_relation(relations, app_id, host_id)

instance_yaml = """
instances
   - instance_type: "$check_name_lower"
     url: "http://address:8080/of/some/rest/api"
     password: admin
     username: admin
     source_identifier: "urn:$check_name_lower:"
     min_collection_interval": 30
"""