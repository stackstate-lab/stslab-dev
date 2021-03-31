from stackstate_checks.base import AgentCheck, ConfigurationError, TopologyInstance


class AcmeCheck(AgentCheck):
    # Components types in STS. See https://localhost:7070/#/settings/component_types
    SERVICE_COMP_TYPE_ID = "urn:stackpack:common:component-type:service"
    APP_COMP_TYPE_ID = "urn:stackpack:common:component-type:application"

    def __init__(self, name, init_config, agentConfig, instances=None):
        AgentCheck.__init__(self, name, init_config, agentConfig, instances)

    def get_instance_key(self, instance):
        if "url" not in instance:
            raise ConfigurationError("Missing url in topology instance configuration.")

        # The check will send information to an instance of the Custom Synchronization StackPack
        # See http://localhost:7070/#/stackpacks/autosync/?type=Integrations
        # The "Instance type (source identifier)" field used to setup a new instance must be the same as
        # the type specified below.
        # The same applies to the the url
        instance_type = instance["instance_type"]
        instance_url = instance["url"]
        return TopologyInstance(instance_type, instance_url)

    def build_id(self, sid, instance):
        return "%s/%s" % (instance["source_identifier"], sid)

    def check(self, instance):
        # Call 3rd-party api to receive some record data. This example information about an application
        record = {
            "business_unit": "Banking",
            "service": "InternetBanking",
            "runtime": "Tomcat",
            "server": "SRV001",
            "area": "acceptance",
            "business_owner": "Bart Banker",
        }

        app_name = record["service"]
        app_id = self.build_id(app_name.upper(), instance)
        app_component = {
            "name": app_name,
            "domain": record[
                "business_unit"
            ],  # See STS http://localhost:7070/#/settings/domains
            "layer": "Applications",  # See STS http://localhost:7070/#/settings/layers
            "environment": record[
                "area"
            ].capitalize(),  # See STS http://localhost:7070/#/settings/environments
            "identifiers": [
                app_id
            ],  # See https://docs.stackstate.com/configure/identifiers
            "labels": [
                "businessapp:banking"
            ],  # Assign labels that can be used to create views easier
            "owner": record[
                "business_owner"
            ],  # Extra property to see on component properties
        }

        # Register the component
        self.component(app_id, self.APP_COMP_TYPE_ID, app_component)

        # We can see that the application runs on a server.
        # Say for instance servers are discovered by another integration in StackState like VMWare, AWS or Azure
        # We need to create server component with the correct identifier so StackState will merge the component
        # with the one from VMWare, AWS or Azure
        # The identifier is important for merging.
        # See https://docs.stackstate.com/configure/identifiers

        host_id = "urn:host:/%s" % record["server"].upper()
        server_component = {
            "name": record["server"].upper(),
            "domain": record["business_unit"].capitalize(),
            "layer": "Machines",
            "environment": record["area"].capitalize(),
            "identifiers": [record["server"].upper(), host_id],
            "labels": ["businessapp:banking"],
            "app_server": record["runtime"],  # additional property
        }

        # Besides using a urn for a component like we used for the application component, we can also use a name for the
        # component like 'host' below
        self.component(host_id, "host", server_component)

        # Relate the 2 components based on their names.
        self.relation(
            app_component["name"],
            server_component["name"],
            "runs_on",
            {"any": "additional properties and labels"},
        )
