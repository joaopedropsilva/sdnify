from src.policy import Policy, PolicyTypes


class Parser:
    def __init__(self, topo_schema: dict):
        self._policies = []
        self._netconfig = topo_schema
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
            "default_vlan": {
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

    def _create_rate_limit_acls(self) -> None:
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

    def _map_all_hosts_from(self, datapath: dict) -> dict:
        interfaces = {}

        for index, hostname in enumerate(dp["hosts"], start=1):
            interfaces[index] = {
                "description": f"Virtualized {hostname}",
                "name": hostname,
                "native_vlan": "default_vlan"
            }

        return interfaces

    def _create_stack_links(self) -> None:
        for link in self._netconfig["links"]:
            (origin, dest) = link

            orgin_dp_mapped_ports = \
                    list(map(lambda x: int(x),
                             self._dps[origin]["interfaces"].keys()))

            dest_dp_mapped_ports = \
                    list(map(lambda x: int(x),
                             self._dps[dest]["interfaces"].keys()))

            origin_available_port = max(orgin_dp_mapped_ports) + 1
            dest_available_port = max(dest_dp_mapped_ports) + 1

            self._dps[origin]["interfaces"][origin_available_port] = {
                "description": f"{origin} link to {dest}",
                "stack": {
                    "dp": dest,
                    "port": dest_available_port
                }
            }

            self._dps[dest]["interfaces"][dest_available_port] = {
                "description": f"{dest} link to {origin}",
                "stack": {
                    "dp": origin,
                    "port": origin_available_port
                }
            }

    def _create_dps(self) -> None:
        for index, dp in enumerate(self._netconfig["datapaths"], start=1):
            dp_config = {
                "dp_id": index,
                "hardware": "Open vSwitch"
            }

            if "priority" in dp:
                dp_config["stack"] = {
                    "priority": dp["priority"]
                }

            dp_config["interfaces"] = {
                **self._map_all_hosts_from(datapath=dp)
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

        self._vlans["default_vlan"]["acls_in"] = acl_names

    def build_config(self) -> dict:
        self._create_rate_limit_acls()
        self._create_dps()
        self._create_stack_links()
        self._create_meters()
        self._populate_vlans_acls_in()

        return {
            "acls": self._acls,
            "dps": self._dps,
            "meters": self._meters,
            "vlans": self._vlans
        }

