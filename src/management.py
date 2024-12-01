from mininet.clean import Cleanup
from mininet.cli import CLI
from typing import List
import yaml

from src.utils import File
from src.data import NetworkBuilder, Policy, PolicyTypes, Success, Error


class VirtualNetworkManager:
    def __init__(self):
        topo_schema_path = File.get_config()["topo_schema_path"]
        self._builder = NetworkBuilder(topo_schema_path=topo_schema_path)
        self._net = None

    def generate(self) -> Success | Error:
        (build_result, net) = self._builder.build_network()

        if isinstance(build_result, Success):
            if net is not None:
                self._net = net
                self._net.start()

        return build_result

    def destroy(self) -> Success | Error:
        operation_result = Success.NetworkDestructionOk

        if self._net is not None:
            try:
                self._net.stop()
            except Exception:
                operation_result = Error.NetworkDestructionFailed

        Cleanup()

        return operation_result

    def invoke_cli(self) -> None:
        CLI(self._net)

    def report_state(self) -> None:
        pass

class FlowManager:
    _MIN_BANDWIDTH = 1
    _MAX_BANDWIDTH = 100
    
    def __init__(self):
        self._policies: List[Policy] = []
        self._policy_rules: dict = {}
        self._meters: dict = {}

    def _validate(self, policy: Policy) -> Success | Error:
        if not isinstance(policy.traffic_type, PolicyTypes):
            return Error.InvalidPolicyTrafficType
        
        if policy.bandwidth < self._MIN_BANDWIDTH \
            or policy.bandwidth > self._MAX_BANDWIDTH:
            return Error.InvalidPolicyBandwidth

        return Success.OperationOk

    def update_tables(self, policy: Policy, operation: str) -> Success | Error:
   
        if operation == "create":
            
            if f"{policy.traffic_type.value}" not in self.__config:
                
                rule = self.generate_faucet_config()
                self.__policies.append(policy)
                self.__config[f"{policy.traffic_type.value}"] = []
                
                self.__config[f"{policy.traffic_type.value}"].append(rule["acls"])

                self.__write_config(policy=policy)
            else:
                self.__write_config(policy=policy)

            return Success.PolicyCreationOk
        
        elif operation == "remove":

            self.__policies = [p for p in self.__policies if p.traffic_type != policy.traffic_type]
            
            self._delete_config(policy=policy)
            
            return Success.PolicyDeletionOk
            
        else:
            return Error.UnknownOperation


    def generate_faucet_config(self):
        """
        Gera a configuração completa de ACLs e Meters no formato do Faucet.
        """
        acls = {}
        meters = {}

        for policy in self.__policies:
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

    def __write_config(self, policy: Policy):
       
        try:
            
            try:
                with open("dependencias/etc/faucet.yaml", "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                existing_config = {}

            if f"{policy.traffic_type.value}" in existing_config["acls"]:
                new_bandwidth = policy.bandwidth * 1000
                existing_config["meters"][f"qos_meter_{policy.traffic_type.value}"]["entry"]["bands"][0]["rate"] = new_bandwidth

                with open("dependencias/etc/faucet.yaml", "w") as file:
                    yaml.dump(existing_config, file, sort_keys=False, default_flow_style=False)

            new_faucet_config = self.generate_faucet_config()

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

            with open("dependencias/etc/faucet.yaml", "w") as file:
                file.write(yaml.dump(existing_config_wt_vlans, sort_keys=False, default_flow_style=False))
                file.write("vlans:\n")
                file.write("  test:\n")
                file.write(f"    description: {existing_config['vlans']['test']['description']}\n")
                file.write(f"    vid: {existing_config['vlans']['test']['vid']}\n")
                file.write(f"    acls_in: {yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")

            return Success.ConfigWriteOk

        except Exception as e:
            
            return Error.ConfigWriteFailure
        
        
    def _delete_config(self, policy: Policy):

        acl = f"{policy.traffic_type.value}"
        qos_meter = f"qos_meter_{policy.traffic_type.value}"

        try:
            with open("dependencias/etc/faucet.yaml", "r") as file:
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
        
            
        with open("dependencias/etc/faucet.yaml", "w") as file:
            
            file.write(yaml.dump(existing_config_wt_vlans, sort_keys=False, default_flow_style=False))
            file.write("vlans:\n")
            file.write("  test:\n")
            file.write(f"    description: {existing_config['vlans']['test']['description']}\n")
            file.write(f"    vid: {existing_config['vlans']['test']['vid']}\n")
            file.write(f"    acls_in: {yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")
        
        
        self.__config = {
            "acls": existing_config.get("acls", {}),
            "meters": existing_config.get("meters", {})
        }

    def _process_alerts(self) -> bool:
        return False

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        validation_result = self._validate(policy)
        if isinstance(validation_result, Error):
            return validation_result

        return self.update_tables(policy=policy, 
                                       operation="create")

    def remove(self, policy: Policy) -> Success | Error:
        if not any(p.traffic_type == policy.traffic_type for p in self.__policies):
            return Error.PolicyNotFound  
        
        return self.update_tables(policy=policy,
                                operation="remove")

class Managers:
    def __init__(self):
        self._virtual_network = VirtualNetworkManager()
        self._flow = FlowManager()
        self._is_network_alive = False

    @property
    def virtual_network(self) -> VirtualNetworkManager:
        return self._virtual_network

    @property
    def flow(self) -> FlowManager:
        return self._flow

    @property
    def is_network_alive(self) -> bool:
        return self._is_network_alive

    @is_network_alive.setter
    def is_network_alive(self, network_status: bool) -> None:
        self._is_network_alive = network_status

