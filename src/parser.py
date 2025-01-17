class Parser:
    def __init__(self, netconfig: dict):
        self._netconfig = netconfig
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
                "vid": 100,
                "acls_in": []
            }
        }

    def _create_rate_limits_acls(self) -> None:
        for config in self._netconfig["rate_limits"]:
            port = config["port"]
            rate = config["rate"]
            transport = config["transport"]

            rule = {
                "rule": {
                    "dl_type": "0x800",
                    "nw_proto": 17 if transport == "udp" else 6,
                    "udp_dst": 17 if transport == "udp" else 6,
                    **({"udp_dst": port} if transport == "udp" else {}),
                    **({"tcp_dst": port} if transport == "tcp" else {}),
                    "actions": {
                        "allow": 1,
                        "meter": f"qos_meter_{port}_{rate}_{transport}"
                    },
                }
            }

            self._acls[f"{port}_{rate}_{transport}"] = [rule]

    def _map_all_hosts_from(self, datapath: dict) -> dict:
        interfaces = {}

        for index, hostname in enumerate(datapath["hosts"], start=1):
            interfaces[index] = {
                "description": f"Virtualized {hostname}",
                "name": hostname,
                "native_vlan": "default_vlan"
            }

        return interfaces

    def _create_stack_links(self) -> None:
        for link in self._netconfig["stack_links"]:
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
        for index, config in enumerate(self._netconfig["rate_limits"], start=1):
            port = config["port"]
            rate = config["rate"]
            transport = config["transport"]

            meter_config = {
                "meter_id": index,
                "entry": {
                    "flags": "KBPS",
                    "bands": [
                        {
                            "type": "DROP",
                            "rate": rate * 1000
                        }
                    ],
                },
            }

            self._meters[f"qos_meter_{port}_{rate}_{transport}"] = meter_config

    def _populate_vlans_acls_in(self) -> None:
        acl_names = list(self._acls.keys())
        acl_names.reverse()

        self._vlans["default_vlan"]["acls_in"] = acl_names

    def build_config(self) -> dict:
        self._create_rate_limits_acls()
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

