class AgentCheckMock(object):
    def __init__(self):
        self.components = dict()
        self.relationships = dict()
        self.log = LoggerStub()

    def component(self, id, type, data):
        self.components[id] = {"id": id, "type": type, "data": data}

    def relation(self, source_id, target_id, type, data):
        key = "%s -> %s" % (source_id, target_id)
        self.relationships[key] = {
            "source_id": source_id,
            "target_id": target_id,
            "type": type,
            "data": data,
        }

    def snapshot(self, instance_key):
        return {
            "start_snapshot": False,
            "stop_snapshot": False,
            "instance_key": instance_key,
            "components": self.components.values(),
            "relations": self.relationships.values(),
        }


class LoggerStub(object):
    def debug(self, msg):
        print("debug: %s" % msg)

    def info(self, msg):
        print("info: %s" % msg)

    def error(self, msg):
        print("error: %s" % msg)

    def warning(self, msg):
        print("warning: %s" % msg)
