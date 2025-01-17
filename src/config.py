from json import load
from yaml import dump
from pathlib import Path


class NetConfig:
    @staticmethod
    def _validate_props_as_dict_list_by(property_config: dict, netconfig: dict) -> None:
        prop = property_config["name"] 
        prop_alias = property_config["alias"] 
        inner_props = property_config["inner_props"] 
        optional_props = property_config["optional_props"] 

        if not isinstance(netconfig[prop], list):
            raise TypeError(f"Property \"{prop}\" must be a list")

        if not len(netconfig[prop]):
            return

        for prop_item in netconfig[prop]:
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

    @classmethod
    def _validate_datapaths_from(cls, netconfig: dict) -> None:
        if not isinstance(netconfig["datapaths"], list):
            raise TypeError("Property \"datapaths\" must be a list")

        if not len(netconfig["datapaths"]):
            raise Exception("Property \"datapaths\" must contain at least one datapath")

        cls._validate_props_as_dict_list_by(
            property_config={
                "name": "datapaths",
                "alias": "Datapath",
                "inner_props": [
                    ("name", int, None),
                    ("hosts", list, str)
                ],
                "optional_props": [("priority", int)]
            },
            netconfig=netconfig)

    @classmethod
    def _validate_rate_limits_from(cls, netconfig: dict) -> None:
        if not isinstance(netconfig["rate_limits"], list):
            raise TypeError("Property \"rate_limit\" must be a list")

        if not len(netconfig["rate_limits"]):
            return

        cls._validate_props_as_dict_list_by(
            property_config={
                "name": "rate_limits",
                "alias": "Rate limit",
                "inner_props": [
                    ("port", int, None),
                    ("rate", int, None),
                    ("transport", str, None)
                ],
                "optional_props": []
            },
            netconfig=netconfig)

    @staticmethod
    def _validate_stack_links_from(netconfig: dict) -> None:
        if not isinstance(netconfig["stack_links"], list):
            raise TypeError("Property \"stack_links\" must be a list")

        if not len(netconfig["stack_links"]):
            return

        for (origin, dest) in netconfig["stack_links"]:
            if not isinstance(origin, str) or not isinstance(dest, str):
                raise TypeError("Stack link names must be a string")

    @classmethod
    def validate(cls, netconfig: dict) -> None:
        if "datapaths" not in netconfig:
            raise KeyError("Property \"datapaths\" not in config file")

        if "rate_limits" not in netconfig:
            raise KeyError("Property \"rate_limits\" not in config file")

        if "stack_links" not in netconfig:
            raise KeyError("Property \"stack_links\" not in config file")

        cls._validate_datapaths_from(netconfig)
        cls._validate_rate_limits_from(netconfig)
        cls._validate_stack_links_from(netconfig)

    @staticmethod
    def load_json_from(path: str) -> dict:
        filepath = Path(path, ".json")

        if not filepath.exists():
            raise FileNotFoundError("Config not found!")

        with open(filepath.resolve(), "r") as file:
            return load(file)


class FaucetConfig:
    _FAUCET_PATH = "etc/faucet/faucet.yaml"

    @staticmethod
    def _get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @classmethod
    def update_with(cls, translated_config: dict) -> None:
        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        with open(faucet_path, "w") as file:
            file.write(dump(translated_config, default_flow_style=False))

    @classmethod
    def clear(cls) -> None:
        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        with open(faucet_path, "w") as file:
            file.write(dump(None, default_flow_style=False))

