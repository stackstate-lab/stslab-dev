from $check_pkg import $class_name
from stackstate_checks.stubs import topology


def test_$check_name_lower():
    instance = {
        "instance_type": "$check_name_lower",
        "url": "http://address:8080/of/some/rest/api",
        "password": "admin",
        "username": "admin",
        "source_identifier": "urn:$check_name_lower:",
        "min_collection_interval": "30",
    }

    check = $class_name("$check_name_lower", {}, {}, instances=[instance])
    check.check(instance)
    snapshot = topology.get_snapshot("")
    components = snapshot["components"]
    relations = snapshot["relations"]

    assert len(components) == 2
    assert components[0]["id"] == "urn:$check_name_lower:/INTERNETBANKING"
    assert components[1]["id"] == "urn:host:/SRV001"
    assert len(relations) == 1
