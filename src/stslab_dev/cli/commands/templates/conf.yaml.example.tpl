init_config:

instances:
  - url: "http://address:8080/of/some/rest/api"
    instance_type: $check_name_lower
    source_identifier: "urn:$check_name_lower:"
    password: admin
    username: admin
    min_collection_interval: 30
