from json import load
from pathlib import Path


class Validator:
    def __init__(self):
        self._netconfig = {}

    def _validate_props_as_dict_list_by(self, property_config: dict):
        prop = property_config["name"] 
        prop_alias = property_config["alias"] 
        inner_props = property_config["inner_props"] 
        optional_props = property_config["optional_props"] 

        if not isinstance(self._netconfig[prop], list):
            raise TypeError(f"Property \"{prop}\" must be a list")

        if not len(self._netconfig[prop]):
            return

        for prop_item in self._netconfig[prop]:
            if not isinstance(prop_item, dict):
                raise TypeError(f"{prop_alias} must be of type dict")

            for (inner, inner_type, on_list_type) in inner_props: 
                if inner not in prop_item:
                    raise KeyError(f"{prop_alias} object must define a \"{inner}\"")

                if not isinstance(prop_item[inner], inner_type):
                    raise TypeError(f"{prop_alias} \"{inner}\" must be a {repr(inner_type)}")

                if isinstance(inner_type, list):
                    for value in prop_item[inner]:
                        if not isinstance(value, on_list_type):
                            raise TypeError(f"{prop_alias} \"{inner}\" must be a {repr(on_list_type)}")

            for (optional, inner_type) in optional_props:
                if not isinstance(prop_item[optional], inner_type):
                    raise TypeError(f"{prop_alias} \"{optional}\" must be a {repr(inner_type)}")

    def _validate_datapaths(self):
        if not isinstance(self._netconfig["datapaths"], list):
            raise TypeError("Property \"datapaths\" must be a list")

        if not len(self._netconfig["datapaths"]):
            raise Exception("Property \"datapaths\" must contain at least one datapath")

        self._validate_props_as_dict_list_by(
            property_config={
                "name": "datapaths",
                "alias": "Datapath",
                "inner_props": [
                    ("name", int, None),
                    ("hosts", list, str)
                ],
                "optional_props": [("priority", int)]
            })

    def _validate_rate_limits(self):
        if not isinstance(self._netconfig["rate_limits"], list):
            raise TypeError("Property \"rate_limit\" must be a list")

        if not len(self._netconfig["rate_limits"]):
            return

        self._validate_props_as_dict_list_by(
            property_config={
                "name": "rate_limits",
                "alias": "Rate limit",
                "inner_props": [
                    ("port", int, None),
                    ("rate", int, None),
                    ("transport", str, None)
                ],
                "optional_props": []
            })

    def _validate_stack_links(self):
        if not isinstance(self._netconfig["stack_links"], list):
            raise TypeError("Property \"stack_links\" must be a list")

        if not len(self._netconfig["stack_links"]):
            return

        for (origin, dest) in self._netconfig["stack_links"]:
            if not isinstance(origin, str) or not isinstance(dest, str):
                raise TypeError("Stack link names must be a string")

    def load_from(self, path: str) -> None:
        if not Path(path).exists():
            raise FileNotFoundError("netconfig.json not found!")

        with open(Path(path).resolve(), "r") as file:
            return load(file)

    def validate(self) -> None:
        if "datapaths" not in self._netconfig:
            raise KeyError("Property \"datapaths\" not in config file")

        if "rate_limits" not in self._netconfig:
            raise KeyError("Property \"rate_limits\" not in config file")

        if "stack_links" not in self._netconfig:
            raise KeyError("Property \"stack_links\" not in config file")

        self._validate_datapaths()
        self._validate_rate_limits()
        self._validate_stack_links()

