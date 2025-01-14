from src.policy import Policy, PolicyTypes
from typing import List
from src.topology import Topology


class Context:
    def __init__(self,
                 policies: List[Policy],
                 topo_schema: dict):
        self._policies = policies
        self._topo_schema = topo_schema
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
        self._dps = {}
        self._meters = {}
        self._vlans = {
            "test": {
                "description": "vlan test",
                "vid": 100
            }
        }

    @property
    def policies(self) -> List[Policy]:
        return self._policies

    @policies.setter
    def policies(self, new_policies: List[Policy]) -> None:
        self._policies = new_policies

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

    def _map_all_hosts_from(self, dp: dict) -> tuple[dict, int]:
        interfaces = {}

        last_port_mapped = 0
        for host in dp["hosts"]:
            last_port_mapped += 1
            interfaces[last_port_mapped] = {
                "description": f"Virtualized {host['name']}",
                "name": host["name"],
                "native_vlan": host["vlan"]
            }

        return interfaces, last_port_mapped

    def _map_all_stacks_from(self, dp: dict, last_port_mapped: int) -> dict:
        stacks = {}

        port = last_port_mapped
        for stack in dp["stack_definitions"]:
            port += 1
            stacks[port] = {
                "description": stack["description"],
                "stack": {
                    "dp": stack["dp"],
                    "port": stack["port"]
                }
            }

        return stacks

    def _create_dps(self) -> None:
        for index, dp in enumerate(self._topo_schema["dps"], start=1):
            dp_config = {
                "dp_id": index,
                "hardware": "Open vSwitch"
            }

            stack_config = {}
            if "stack_priority" in dp:
                stack_config = {"priority": dp["stack_priority"]}

            dp_config["stack"] = {
                **stack_config
                }

            (hosts, last_port_mapped) = self._map_all_hosts_from(dp=dp)
            stacks = self._map_all_stacks_from(dp=dp,
                                               last_port_mapped=last_port_mapped)

            dp_config["interfaces"] = {
                **hosts,
                **stacks
            }

            self._dps[dp["name"]] = dp_config

    def _create_meters(self) -> None:
        for index, policy in enumerate(self._policies, start=1):
            bandwidth = policy.bandwidth * 1000

            meter_config = {
                "meter_id": index,
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
        self._create_dps()
        self._create_meters()
        self._populate_vlans_acls_in()

        return {
            "acls": self._acls,
            "dps": self._dps,
            "meters": self._meters,
            "vlans": self._vlans
        }


class ContextFactory:
    @staticmethod
    def create_from(context_data: dict) -> tuple[str, Context | None]:
        try:
            topology = context_data["topology"]
        except KeyError:
            return ("Informação de topologia ausente.", None)

        if not isinstance(topology, Topology):
            return ("Topologia inválida para criação de arquivo de configuração.",
                    None)

        if not topology.is_valid:
            return ("Topologia inválida para criação de arquivo de configuração.",
                    None)

        try:
            policies = context_data["policies"]
        except KeyError:
            policies = []

        if not isinstance(policies, list):
            policies = []

        return ("", Context(policies=policies,
                            topo_schema=topology.schema))

