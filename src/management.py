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

    def _update_tables(self, policy: Policy, operation: str) -> Success | Error:
        if operation == "create":
            if f"{policy.traffic_type}-traffic" not in self._policy_rules:
                self._policy_rules[f"{policy.traffic_type}-traffic"] = []

            self._policy_rules[f"{policy.traffic_type}-traffic"] \
                .append(self._create_rule(policy=policy))

            self._write_config()

            self._policies.append(policy)

            return Success.PolicyCreationOk
        elif operation == "delete":
            if not any(p.traffic_type == policy.traffic_type
                       for p in self._policies):
                    return Error.PolicyNotFound

            self._policies = [p for p in self._policies
                               if p.traffic_type != policy.traffic_type]
            if f"{policy.traffic_type}-traffic" in self._policy_rules:
                del self._policy_rules[f"{policy.traffic_type}-traffic"]

            meter_name = f"qos_meter_{policy.traffic_type}"
            if meter_name in self._meters:
                del self._meters[meter_name]

            self._write_config()

            return Success.PolicyDeletionOk
        else:
            return Error.UnknownOperation

    def _create_rule(self, policy: Policy) -> dict:
        """
        Cria a regra de tráfego baseada na política.
        """
        meter_name, meter_config = self._create_meter(policy)
        self._meters[meter_name] = meter_config

        return {
            "acl_name": policy.traffic_type,
            "rules": [
                {
                    "dl_type": "0x800",
                    "nw_proto": 17 if policy.traffic_type == PolicyTypes.VOIP else 6,
                    "udp_dst": 20000 if policy.traffic_type == PolicyTypes.VOIP else None,
                    "tcp_dst": 80 if policy.traffic_type == PolicyTypes.HTTP \
                                  else 21 if policy.traffic_type == PolicyTypes.FTP \
                                  else None,
                    "actions": {
                        "allow": 1,
                        "meter": meter_name
                    }
                }
            ]
        }

    def _create_meter(self, policy: Policy) -> tuple[str, dict]:
        """
        Cria a configuração de um meter com base na política.
        """
        bandwidth = (policy.bandwidth / 100) * self._MAX_BANDWIDTH * 1000000

        meter_name = f"qos_meter_{policy.traffic_type}"

        meter_config = {
            "name": meter_name,
            "rates": [{"rate": bandwidth, "unit": "bits_per_second"}]
        }

        return meter_name, meter_config

    def _generate_faucet_config(self):
        """
        Gera a configuração completa de ACLs e Meters no formato do Faucet.
        """
        acls = []
        meters = {}
        
        for policy in self._policies:
            # Create meter
            meter_name, meter_config = self._create_meter(policy)
            meters[meter_name] = meter_config
            
            # Create ACL rule
            acl_rule = self._create_rule(policy)
            
            # Append the ACL rule
            acls.append({
                "acl_name": policy.traffic_type,
                "rules": acl_rule["rules"]
            })
        
        return {
            "acls": acls,
            "meters": meters
        }

    def _write_config(self):
        """
        Atualiza o arquivo faucet.yaml com o conteúdo de self._policy_rules,
        mantendo as entradas já existentes.
        """
        try:
            existing_config = {}
            faucet_config = self._generate_faucet_config()
            
            try:
                with open("faucet.yaml", "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                pass
            
            faucet_yaml_config = {
                "acls": faucet_config.get("acls", []),
                "meters": faucet_config.get("meters", {})
            }
            
            existing_config.update(faucet_yaml_config)
            
            with open("faucet.yaml", "w") as file:
                yaml.dump(existing_config, file, default_flow_style=False)
            
            return Success.ConfigWriteOk
        
        except Exception:
            return Error.ConfigWriteFailure

    def _process_alerts(self) -> bool:
        return False

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        validation_result = self._validate(policy)
        if isinstance(validation_result, Error):
            return validation_result
        
        return self._update_tables(policy=policy,
                                   operation="create")

    def remove(self, policy: Policy) -> Success | Error:
        return self._update_tables(policy=policy,
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

