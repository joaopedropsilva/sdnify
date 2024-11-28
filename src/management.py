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
                self._policy_rules[f"{policy.traffic_type.value}-traffic"] = []

            self._policy_rules[f"{policy.traffic_type.value}-traffic"] \
                .append(self._create_rule(policy=policy))

            self._policies.append(policy)

            self._write_config()

            return Success.PolicyCreationOk
        elif operation == "delete":
            if not any(p.traffic_type == policy.traffic_type
                       for p in self._policies):
                    return Error.PolicyNotFound

            self._policies = [p for p in self._policies
                               if p.traffic_type != policy.traffic_type]
            if f"{policy.traffic_type.value}-traffic" in self._policy_rules:
                del self._policy_rules[f"{policy.traffic_type.value}-traffic"]

            meter_name = f"qos_meter_{policy.traffic_type.value}"
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
            "acl_name": policy.traffic_type.value,
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

        meter_name = f"qos_meter_{policy.traffic_type.value}"

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
            meter_name, meter_config = self._create_meter(policy)
            meters[meter_name] = meter_config
            
            acl_rule = self._create_rule(policy)
            
            acls.append({
                "acl_name": policy.traffic_type.value,
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
        faucet_yml_file = File.get_config()["faucet_config_path"]
        existing_config = {}

        try:
            try:
                with open(faucet_yml_file, "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                existing_config = {}
            
            new_faucet_config = self._generate_faucet_config()
            
            # Remover ACLs obsoletas (não estão na nova configuração)
            existing_config["acls"] = [
                acl for acl in existing_config.get("acls", [])
                if acl.get("acl_name") in [new_acl.get("acl_name") for new_acl in new_faucet_config.get("acls", [])]
            ]

            # Remover meters obsoletos (não estão sendo mais referenciados)
            referenced_meters = {
                rule.get("actions", {}).get("meter")
                for acl in new_faucet_config.get("acls", [])
                for rule in acl.get("rules", [])
                if rule.get("actions", {}).get("meter")
            }

            existing_config["meters"] = {
                name: config
                for name, config in existing_config.get("meters", {}).items()
                if name in referenced_meters
            }

            # Atualizar a configuração com os novos meters e ACLs
            # Atualiza os Meters
            existing_config["meters"].update(new_faucet_config.get("meters", {}))

            # Atualiza as ACLs
            if "acls" not in existing_config:
                existing_config["acls"] = []
            
            # Remover regras existentes para o mesmo nome de ACL
            existing_config["acls"] = [
                acl for acl in existing_config["acls"]
                if acl.get('acl_name') not in [new_acl.get('acl_name') for new_acl in new_faucet_config.get('acls', [])]
            ]

            # Adiciona as novas ACLs
            existing_config["acls"].extend(new_faucet_config.get("acls", []))

            with open(faucet_yml_file, "w") as file:
                yaml.dump(existing_config, file, default_flow_style=False)
            
            return Success.ConfigWriteOk
        except Exception:
            # Log the error or handle it appropriately
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

