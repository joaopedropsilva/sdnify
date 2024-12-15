from pathlib import Path
from enum import Enum
from typing import List
import json
import yaml

from src.policy import PolicyTypes, Policy


class _Messages(Enum):
    ErrorConfigNotFound = "Arquivo de configuração não encontrado."
    ErrorCouldNotReadConfig = "Não foi possível ler o arquivo de configuração."


class Config:
    _CFG_FILENAME = "config.json"
    _CFG_EXAMPLE_FILENAME = "config.example.json"

    @staticmethod
    def _get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @staticmethod
    def _read_from(path: Path) -> tuple[str, dict]:
        is_json = True if str(path).find("json") != -1 else False

        try:
            with open(path, "r") as file:
                if is_json:
                    return "", json.load(file)
                
                return "", yaml.safe_load(file)
        except FileNotFoundError:
            return _Messages.ErrorConfigNotFound.value, {}
        except (yaml.YAMLError, json.JSONDecodeError):
            return _Messages.ErrorCouldNotReadConfig.value, {}

    @classmethod
    def get(cls) -> tuple[str, dict]:
        config_path = Path(
            cls._get_project_path(),
            cls._CFG_FILENAME
        )
        config_example_path = Path(
            cls._get_project_path(),
            cls._CFG_EXAMPLE_FILENAME
        )


        (err, config) = cls._read_from(path=config_path)
        if err != "":
            return cls._read_from(path=config_example_path)

        return "", config


class _Context:
    def __init__(self, policies: List[Policy], redirect: List[dict]):
        self._policies = policies
        self._redirect = redirect
        self._acls = {
            "allow-all": [
                {
                    "rule": {
                        "actions": {
                            "allow": 1
                        }
                    }
                }
            ],
        }
        self._meters = {}
        self._vlans = {
            "test": {
                "description": "vlan test",
                "vid": 100
            }
        }

    def _get_protocol_by(self, traffic_type: str) -> dict:
        if traffic_type == PolicyTypes.VOIP.value:
            proto_number = 17
        elif traffic_type != PolicyTypes.VOIP.value \
                and traffic_type != "all":
            proto_number = 6
        else:
            proto_number = 0

        return {
            **({"nw_proto": proto_number} \
                    if proto_number != 0 \
                    else {})
        }

    def _get_ports_by(self, traffic_type: str) -> dict:
        return {
            **({"udp_dst": 5001} \
                if traffic_type == PolicyTypes.VOIP.value \
                else {}),
            **({"tcp_dst": 80} \
               if traffic_type == PolicyTypes.HTTP.value \
               else {}),
            **({"tcp_dst": 21} \
               if traffic_type == PolicyTypes.FTP.value \
               else {}),
        }

    def _create_policies_acls(self) -> None:
        for policy in self._policies:
            rule = {
                "rule": {
                    "dl_type": '0x800',
                    **self._get_protocol_by(
                        traffic_type=policy.traffic_type.value),
                    **self._get_ports_by(
                        traffic_type=policy.traffic_type.value),
                    "actions": {
                        "allow": 1,
                        "meter": f"qos_meter_{policy.traffic_type.value}"
                    },
                }
            }

            self._acls[policy.traffic_type.value] = [rule]

    def _create_redirect_acls(self) -> None:
        for config in self._redirect:
            src = config["src_name"]
            dst = config["dst_name"]
            traffic_type = config["traffic_type"]

            rule = {
                "rule": {
                    "dl_type": '0x800',
                    **self._get_protocol_by(traffic_type=traffic_type),
                    **self._get_ports_by(traffic_type=traffic_type),
                    "actions": {
                        "allow": 1,
                        "output": {
                            "set_fields": [
                                {
                                    "ipv4_dst": config["dst_ip"]
                                }
                            ]
                        }
                    }
                }
            }

            acl_name = f"{src}_{dst}_{traffic_type}"
            if acl_name not in self._acls:
                self._acls[acl_name] = []
            self._acls[acl_name].append(rule)

    def _create_meters(self) -> None:
        for policy in self._policies:
            bandwidth = policy.bandwidth * 1000

            meter_config = {
                "meter_id": len(self._meters) + 1,
                "entry": {
                    "flags": "KBPS",
                    "bands": [
                        {
                            "type": "DROP",
                            "rate": bandwidth
                        }
                    ],
                },
            }

            self._meters[f"qos_meter_{policy.traffic_type.value}"] = \
                    meter_config

    def _populate_vlans_acls_in(self) -> None:
        acl_names = list(self._acls.keys())
        acl_names.reverse()

        self._vlans["test"]["acls_in"] = acl_names

    def build_config(self) -> dict:
        self._create_policies_acls()
        self._create_redirect_acls()
        self._create_meters()
        self._populate_vlans_acls_in()

        return {
            "acls": self._acls,
            "meters": self._meters,
            "vlans": self._vlans
        }


class _ContextFactory:
    @staticmethod
    def create_from(context_data: dict) -> _Context:
        try:
            policies = context_data["policies"]
        except KeyError:
            policies = []

        try:
            redirect = context_data["redirect"]
        except KeyError:
            redirect = []

        return _Context(policies=policies, redirect=redirect)


class FaucetConfig(Config):
    _FAUCET_PATH = "etc/faucet/faucet.yaml"

    @classmethod
    def get(cls) -> tuple[str, dict]:
        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        return cls._read_from(path=faucet_path)

    @classmethod
    def update_based_on(cls, context_data: dict) -> tuple[str, bool]:
        (err, existing_config) = cls.get()

        if err != "":
            return err, False

        context = _ContextFactory.create_from(context_data=context_data)

        config = context.build_config()

        config["dps"] = {
            **existing_config.get("dps", {})
        }

        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        with open(faucet_path, "w") as file:
            file.write(yaml.dump(config, default_flow_style=False))

        return "", True

