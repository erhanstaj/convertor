class TypeAnalyzer:
    def __init__(self, config: dict):
        self.basic_types = set(config.get("types", {}).get("basic_types", []))
        self.remove_prefix = config.get("naming", {}).get("remove_prefix", "msg").lower()

    def is_basic(self, type_name: str) -> bool:
        return type_name.lower().strip() in self.basic_types

    def map_type_name(self, type_name: str) -> str:
        prefix_capitalized = self.remove_prefix.capitalize()
        if type_name.startswith(prefix_capitalized):
            return type_name.replace(prefix_capitalized, "Struct", 1)
        return type_name
