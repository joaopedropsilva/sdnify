from typing import List
from pathlib import Path
import yaml

from src.utils import File
from src.data import Success, Error
from src.policy import Policy, PolicyTypes
from src.virtnet import VirtNet


class FlowManager:
    _MIN_BANDWIDTH = 1
    
    def __init__(self):
        self._project_config = File.get_config()
        self._policies: List[Policy] = []
        self._config: dict = {}

    def _update_tables(self, policy: Policy, operation: str) -> Success | Error:
        # Alterar essa lógica para não fazer tudo aqui
        if operation == "create":
            
            if f"{policy.traffic_type.value}" not in self._config:
                
                self._policies.append(policy)

                rule = self._generate_faucet_config()

                self._config[f"{policy.traffic_type.value}"] = []
                
                self._config[f"{policy.traffic_type.value}"].append(rule["acls"])

                self._write_config(policy=policy)
            else:
                self._write_config(policy=policy)

            return Success.PolicyCreationOk
        
        elif operation == "remove":

            self._policies = [p for p in self._policies if p.traffic_type != policy.traffic_type]
            
            self._delete_config(policy=policy)
            
            return Success.PolicyDeletionOk
            
        else:
            return Error.UnknownOperation


    def _generate_faucet_config(self):
        """
        Gera a configuração completa de ACLs e Meters no formato do Faucet.
        """
        acls = {}
        meters = {}

        for policy in self._policies:
            reserved_bandwidth = policy.bandwidth * 1000

            meter_name = f"qos_meter_{policy.traffic_type.value}"
            meter_config = {
                "meter_id": len(meters) + 1, 
                "entry": {
                    "flags": "KBPS",
                    "bands": [{"type": "DROP", "rate": reserved_bandwidth}],
                },
            }

            rule = {
                "rule":{
                "dl_type": '0x800',
                "nw_proto": 17 if policy.traffic_type == PolicyTypes.VOIP else 6,
                **({"udp_dst": 5001} if policy.traffic_type == PolicyTypes.VOIP else {}),
                **({"tcp_dst": 80} if policy.traffic_type != PolicyTypes.VOIP else {}),
                **({"tcp_dst": 21} if policy.traffic_type == PolicyTypes.FTP else {}),
                "actions": {"allow": 1, "meter": meter_name},
                }
                
            }
            
            meters[meter_name] = meter_config
            
            acl_name = policy.traffic_type.value
            if acl_name not in acls:
                acls[acl_name] = []
           
            acls[acl_name].append(rule)

        return {"acls": acls, "meters": meters}

    def _write_config(self, policy: Policy):
        faucet_path = Path(File.get_project_path(),
                           "dependencies/etc/faucet/faucet.yaml")

        try:
            try:
                with open(faucet_path, "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                existing_config = {}

            if f"{policy.traffic_type.value}" in existing_config["acls"]:
                new_bandwidth = policy.bandwidth * 1000
                existing_config["meters"][f"qos_meter_{policy.traffic_type.value}"]["entry"]["bands"][0]["rate"] = new_bandwidth

                with open(faucet_path, "w") as file:
                    yaml.dump(existing_config, file, sort_keys=False, default_flow_style=False)

            new_faucet_config = self._generate_faucet_config()

            existing_config["acls"] = {
                **existing_config.get("acls", {}),
                **new_faucet_config["acls"],
            }

            existing_config["meters"] = {
                **existing_config.get("meters", {}),
                **new_faucet_config["meters"],
            }

            acl_names = list(existing_config["acls"].keys())
            acl_names.reverse()

            existing_config["vlans"]["test"]["acls_in"] = acl_names
            existing_config_wt_vlans = existing_config.copy()
            del existing_config_wt_vlans["vlans"]

            with open(faucet_path, "w") as file:
                file.write(yaml.dump(existing_config_wt_vlans, sort_keys=False, default_flow_style=False))
                file.write("vlans:\n")
                file.write("  test:\n")
                file.write(f"    description: {existing_config['vlans']['test']['description']}\n")
                file.write(f"    vid: {existing_config['vlans']['test']['vid']}\n")
                file.write(f"    acls_in: {yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")

            return Success.ConfigWriteOk

        except Exception:
            return Error.ConfigWriteFailure
        
    def _delete_config(self, policy: Policy):
        faucet_path = Path(File.get_project_path(),
                           "dependencies/etc/faucet/faucet.yaml")

        acl = f"{policy.traffic_type.value}"
        qos_meter = f"qos_meter_{policy.traffic_type.value}"

        try:
            with open(faucet_path, "r") as file:
                existing_config = yaml.safe_load(file) or {}
        except FileNotFoundError:
                existing_config = {}
        
        del existing_config["acls"][acl]
        del existing_config["meters"][qos_meter]

        acl_names = list(existing_config["acls"].keys())
        acl_names.reverse()

        existing_config["vlans"]["test"]["acls_in"] = acl_names
        existing_config_wt_vlans = existing_config.copy()
        del existing_config_wt_vlans["vlans"]
            
        with open(faucet_path, "w") as file:
            
            file.write(yaml.dump(existing_config_wt_vlans, sort_keys=False, default_flow_style=False))
            file.write("vlans:\n")
            file.write("  test:\n")
            file.write(f"    description: {existing_config['vlans']['test']['description']}\n")
            file.write(f"    vid: {existing_config['vlans']['test']['vid']}\n")
            file.write(f"    acls_in: {yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")
        
        self._config = {
            "acls": existing_config.get("acls", {}),
            "meters": existing_config.get("meters", {})
        }

    def process_alerts(self, alerts: dict) -> Success | Error:
        return Success.OperationOk

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        return self._update_tables(policy=policy,
                                   operation="create")

    def remove_policy_by(self, traffic_type: PolicyTypes) -> Success | Error:
        if not any(p.traffic_type == traffic_type \
                   for p in self._policies):
            return Error.PolicyNotFound  
        

        temp_policy = Policy(traffic_type=traffic_type,
                             bandwidth=30)

        return self._update_tables(policy=temp_policy, operation="remove")

class NetworkManager:
    def __init__(self):
        self._flow = FlowManager()

    @property
    def flow(self) -> FlowManager:
        return self._flow


class VirtNetManager(NetworkManager):
    def __init__(self):
        super().__init__()
        self._virtnet = VirtNet()

    @property
    def virtnet(self) -> VirtNet:
        return self._virtnet

    @property
    def network_already_up(self) -> bool:
        return True if self._virtnet.net is not None else False

