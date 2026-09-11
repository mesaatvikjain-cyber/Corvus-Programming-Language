import json

# Corvus Native JSON Serialization Module (v4.2)

class JSONEngine:
    @staticmethod
    def parse(json_str):
        if not isinstance(json_str, str):
            json_str = str(json_str)
        return json.loads(json_str)

    @staticmethod
    def stringify(obj, indent=None):
        return json.dumps(obj, indent=indent)

_global_json_engine = JSONEngine()
