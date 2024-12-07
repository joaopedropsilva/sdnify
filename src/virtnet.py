from mininet.node import RemoteController
from mininet.clean import Cleanup
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.net import Mininet
from pathlib import Path
import yaml

from src.utils import File
from src.data import Error, Success


class CustomTopo(Topo):
    def build(self, topo_schema: dict) -> None:
        for host in topo_schema["hosts"]:
            self.addHost(host)

        for switch in topo_schema["switches"]:
            id = switch["id"]
            links = switch["links"]

            self.addSwitch(id)

            for host in links:
                self.addLink(host, id)


class VirtNetBuilder():
    _DEFAULT_CONTROLLER_NAME = "c0"
    _DEFAULT_CONTROLLER_IP = "faucet"
    _DEFAULT_OPF_PORT = 6653
    _TS_SWITCHES_KEY = "switches"
    _TS_HOSTS_KEY = "hosts"
    _TS_ID_KEY = "id"
    _TS_LINKS_KEY = "links"

    def __init__(self, topo_schema_path: str, controller_options: dict = {}):
        self._topo_schema_path = topo_schema_path
        self._controller_name = controller_options["name"] \
                                    if len(controller_options) \
                                    else self._DEFAULT_CONTROLLER_NAME
        self._controller_ip = controller_options["ip"] \
                                   if len(controller_options) \
                                    else self._DEFAULT_CONTROLLER_IP
        self._opf_port = controller_options["opf_port"] \
                                    if len(controller_options) \
                                    else self._DEFAULT_OPF_PORT

    def _create_controller(self) -> RemoteController:
        return RemoteController(
            name=self._controller_name,
            ip=self._controller_ip,
            port=self._opf_port
        )

    def _validate_topo(self,
                        schema: dict) \
                        -> Success | Error:
        if not isinstance(schema[self._TS_HOSTS_KEY], list):
            return Error.HostsKeyWrongTypeInTopoSchema
        
        for host in schema[self._TS_HOSTS_KEY]:
            if not isinstance(host, str):
                return Error.HostsKeyWrongValueInTopoSchema
        
        if not isinstance(schema[self._TS_SWITCHES_KEY], list):
            return Error.SwitchesKeyWrongTypeInTopoSchema
        
        for switch in schema[self._TS_SWITCHES_KEY]:
            if not isinstance(switch, dict):
                return Error.SwitchesKeyWrongValueInTopoSchema

            if self._TS_ID_KEY not in switch \
                or not isinstance(switch[self._TS_ID_KEY], str):
                return Error.SwitchObjectWithNoIdInTopoSchema

            if self._TS_LINKS_KEY not in switch \
                or not isinstance(switch[self._TS_LINKS_KEY], list):
                return Error.SwitchObjectWithNoLinksInTopoSchema
            
            for link in switch[self._TS_LINKS_KEY]:
                if not isinstance(link, str):
                    return Error.LinksWrongValueInTopoSchema

        return Success.OperationOk

    def _translate_topo_to_controller_config(self,
                                             topo_schema: dict) \
                                             -> Success | Error:
        faucet_path = Path(File.get_project_path(),
                           "dependencies/etc/faucet/faucet.yaml")

        try:
            with open(faucet_path, "r") as file:
                existing_config = yaml.safe_load(file)
        except FileNotFoundError:
            return Error.ControllerConfigNotFound

        dps = {}
        for dp_number, switch in enumerate(topo_schema[self._TS_SWITCHES_KEY],
                                           start=1):
            id = switch[self._TS_ID_KEY]
            hosts = switch[self._TS_LINKS_KEY]

            interfaces = {}
            for opf_port, host in enumerate(hosts, start=1):
                interfaces[opf_port] = {
                    "name": host,
                    "description": f"virtualized {host}",
                    "native_vlan": f"test"
                }

            dps[id] = {
                "dp_id": dp_number,
                "hardware": "Open vSwitch",
                "interfaces": interfaces
            }

        existing_config["dps"] = dps

        try:
            acl_names = list(existing_config["acls"].keys())
            acl_names.reverse()

            existing_config["vlans"]["test"]["acls_in"] = acl_names
            existing_config_wt_vlans = existing_config.copy()
            del existing_config_wt_vlans["vlans"]

            with open(faucet_path, "w") as file:
                file.write(yaml.dump(existing_config_wt_vlans,
                                     sort_keys=False,
                                     default_flow_style=False))
                file.write("vlans:\n")
                file.write("  test:\n")
                file.write(f"    description: " \
                           f"{existing_config['vlans']['test']['description']}\n")
                file.write(f"    vid: " \
                           f"{existing_config['vlans']['test']['vid']}\n")
                file.write(f"    acls_in: " \
                           f"{yaml.dump(existing_config['vlans']['test']['acls_in'], default_flow_style=True).strip()}\n")
        except Exception:
            return Error.ConfigWriteFailure
        
        return Success.ConfigWriteOk

    def build_network(self) -> tuple[Success | Error, Mininet | None]:
        topo_schema = File.read_json_from(self._topo_schema_path)

        validation_result = self._validate_topo(schema=topo_schema)
        if not isinstance(validation_result, Success):
            return (validation_result, None)

        translation_result = \
            self._translate_topo_to_controller_config(topo_schema=topo_schema)
        if not isinstance(translation_result, Success):
            return (translation_result, None)

        net = None
        build_result = None
        try:
            net = Mininet(topo=CustomTopo(topo_schema=topo_schema),
                          controller=self._create_controller())
            build_result = Success.NetworkBuildOk
        except Exception:
            build_result = Error.NetworkBuildFailed

        return (build_result, net)


class VirtNet:
    def __init__(self):
        topo_schema_path = File.get_config()["topo_schema_path"]
        self._builder = VirtNetBuilder(topo_schema_path=topo_schema_path)
        self._net = None

    @property
    def net(self) -> Mininet | None:
        return self._net

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

    def stats(self) -> None:
        return

