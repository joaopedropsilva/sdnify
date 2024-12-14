from pathlib import Path
from enum import Enum
import json
import yaml

from src.policy import PolicyTypes


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


class FaucetConfig(Config):
    _FAUCET_PATH = "dependencies/etc/faucet/faucet.yaml"

    @staticmethod
    def _create_rate_limit_from(context: dict) -> dict:
        """
        Gera a configuração completa de ACLs e Meters no formato do Faucet.
        """

        policies = context["policies"]

        acls = {}
        meters = {}

        for policy in policies:
            bandwidth = policy.bandwidth * 1000

            meter_name = f"qos_meter_{policy.traffic_type.value}"
            meter_config = {
                "meter_id": len(meters) + 1,
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

            meters[meter_name] = meter_config

            acl = {
                "rule":{
                    "dl_type": '0x800',
                    "nw_proto": 17 \
                        if policy.traffic_type == PolicyTypes.VOIP \
                        else 6,
                    **({"udp_dst": 5001} \
                        if policy.traffic_type == PolicyTypes.VOIP \
                        else {}),
                    **({"tcp_dst": 80} \
                       if policy.traffic_type != PolicyTypes.VOIP \
                       else {}),
                    **({"tcp_dst": 21} \
                       if policy.traffic_type == PolicyTypes.FTP \
                       else {}),
                    "actions": {
                        "allow": 1,
                        "meter": meter_name
                    },
                }
            }

            acl_name = policy.traffic_type.value
            if acl_name not in acls:
                acls[acl_name] = []

            acls[acl_name].append(acl)

        return {"acls": acls, "meters": meters}

    @classmethod
    def get(cls) -> tuple[str, dict]:
        faucet_path = Path(
            cls._get_project_path(),
            cls._FAUCET_PATH
        )

        return cls._read_from(path=faucet_path)

    @classmethod
    def update_based_on(cls, context: dict) -> tuple[str, bool]:
        (err, existing_config) = cls.get()

        if err != "":
            return err, False

        rate_limit_config = cls._create_rate_limit_from(context=context)

        existing_config["acls"] = {
            **existing_config.get("acls", {}),
            **rate_limit_config["acls"],
        }

        existing_config["meters"] = {
            **existing_config.get("meters", {}),
            **rate_limit_config["meters"],
        }

        acl_names = list(existing_config["acls"].keys()).reverse()

        existing_config["vlans"]["test"]["acls_in"] = acl_names
        existing_config_wt_vlans = existing_config.copy()
        del existing_config_wt_vlans["vlans"]

        faucet_path = Path(
            cls._get_project_path(),
            cls._FAUCET_PATH
        )
        with open(faucet_path, "w") as file:
            file.write(yaml.dump(existing_config_wt_vlans, sort_keys=False, default_flow_style=False))
            file.write("vlans:\n")
            file.write("  test:\n")
            file.write(f"    description: {existing_config['vlans']['test']['description']}\n")
            file.write(f"    vid: {existing_config['vlans']['test']['vid']}\n")
            file.write(f"    acls_in: {yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")

        return "", True

