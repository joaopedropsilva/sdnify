from typing import List

from src.config import FaucetConfig
from src.utils import File
from src.data import Success, Error
from src.policy import Policy, PolicyTypes
from src.virtnet import VirtNet


class FlowManager:
    _MIN_BANDWIDTH = 1
    
    def __init__(self):
        self._project_config = File.get_config()
        self._policies: List[Policy] = []

    def _delete_config(self, policy: Policy):
        from pathlib import Path
        import yaml
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


    def process_alerts(self, alerts: dict) -> Success | Error:
        return Success.OperationOk

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        policy_exist = len([p for p in self._policies \
                            if p.traffic_type == policy.traffic_type]) != 0

        if not policy_exist:
            self._policies.append(policy)

        (_, did_config_update) = \
                FaucetConfig.update_based_on(
                        context={"policies": self._policies})

        if not did_config_update:
            return Error.ConfigWriteFailure

        return Success.ConfigWriteOk

    def remove_policy_by(self, traffic_type: PolicyTypes) -> Success | Error:
        if not any(p.traffic_type == traffic_type \
                   for p in self._policies):
            return Error.PolicyNotFound  

        temp_policy = Policy(traffic_type=traffic_type,
                             bandwidth=30)

        self._policies = [p for p in self._policies
                          if p.traffic_type != temp_policy.traffic_type]

        self._delete_config(policy=temp_policy)

        return Success.OperationOk

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

