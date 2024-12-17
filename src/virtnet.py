from mininet.node import RemoteController
from mininet.clean import Cleanup
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.net import Mininet
import json

from src.config import Config
from src.data import Error, Success


class CustomTopo(Topo):
    def build(self, topo_schema: dict) -> None:
        for dp in topo_schema["dps"]:
            dp_name = dp["name"]

            self.addSwitch(dp_name)

            for host in dp["hosts"]:
                self.addHost(host)
                self.addLink(host, dp_name)


class _TopoSchema:
    def __init__(self, schema: dict):
        self._schema = schema

    def _validate_dps(self) -> tuple[str, bool]:
        if "dps" not in self._schema:
            return ("\"dps\" não encontrado no arquivo de topologia.", False)

        dps = self._schema["dps"]

        if not isinstance(dps, list):
            return ("\"dps\" deve ser do tipo \"list\"", False)

        for dp in dps:
            if not isinstance(dp, dict):
                return ("Tipo não permitido para objeto em \"dps\"", False)

            if "name" not in dp:
                return("Campo \"name\" ausente em objeto de \"dps\"", False)

            try:
                hosts = dp["hosts"]
            except KeyError:
                return("Campo \"hosts\" ausente em objeto de \"dps\"", False)

            if not isinstance(hosts, list):
                return ("\"hosts\" deve ser do tipo \"list\"", False)

            for host in hosts:
                if "name" not in host:
                    return("Campo \"name\" ausente em objeto de \"hosts\"",
                           False)

                if not isinstance(host["name"], str):
                    return("Tipo inválido em \"name\" de objeto em \"hosts\"",
                           False)

                if "vlan" not in host:
                    return("Campo \"vlan\" ausente em objeto de \"hosts\"",
                           False)

                if not isinstance(host["vlan"], str):
                    return("Tipo inválido em \"vlan\" de objeto em \"hosts\"",
                           False)

        return ("", True)

    def _validate_vlans(self) -> tuple[str, bool]:
        if "vlans" not in self._schema:
            return ("\"vlans\" não encontrado no arquivo de topologia.", False)

        vlans = self._schema["vlans"]

        if not isinstance(vlans, list):
            return ("\"vlans\" deve ser do tipo \"list\"", False)

        for vlan in vlans:
            if not isinstance(vlan, dict):
                return ("Tipo não permitido para objeto em \"vlans\"", False)

            if "name" not in vlan:
                return("Campo \"name\" ausente em objeto de \"vlans\"", False)

            if not isinstance(vlan["name"], str):
                return("Tipo inválido em \"name\" de objeto em \"vlans\"",
                       False)

            if "description" not in vlan:
                return("Campo \"description\" ausente em objeto de \"vlans\"",
                       False)

            if not isinstance(vlan["description"], str):
                return("Tipo inválido em \"description\" de objeto em \"vlans\"",
                       False)

        return ("", True)

    def validate(self) -> tuple[str, bool]:
        (err_dps, is_dps_valid) = self._validate_dps()
        if not is_dps_valid:
            return (err_dps, False)

        (err_vlans, is_vlans_valid) = self._validate_vlans()
        if not is_vlans_valid:
            return (err_vlans, False)

        return ("", True)


class _TopoSchemaFactory:
    @staticmethod
    def create() -> tuple[str, _TopoSchema | None]:
        (err, config) = Config.get()

        if err != "":
            return (err, None)

        try:
            topo_schema_path = config["topo_schema_path"]
        except KeyError:
            return ("Caminho para arquivo de topologia não encontrado.", None)

        topo_schema = dict()
        try:
            with open(topo_schema_path, "r") as file:
                json.load(file)
        except FileNotFoundError as err:
            return (str(err), None)
        except json.JSONDecodeError as err:
            return (str(err), None)

        return "", _TopoSchema(schema=topo_schema)


class _VirtNetFactory():
    _OPF_PORT = 6653

    @classmethod
    def create(cls) -> tuple[str, Mininet | None]:
        (err_creation, topo_schema) = _TopoSchemaFactory.create()
        if err_creation != "" or topo_schema is None:
            return (err_creation, None)

        (err_validation, is_valid) = topo_schema.validate()

        if not is_valid:
            return (err_validation, None)

        net = None
        try:
            net = Mininet(topo=CustomTopo(topo_schema=topo_schema))

            net.addController(name="c1",
                              controller=RemoteController,
                              ip="faucet",
                              port=cls._OPF_PORT)

            net.addController(name="c2",
                              controller=RemoteController,
                              ip="gauge",
                              port=cls._OPF_PORT)

            return ("", net)
        except Exception:
            return ("Falha ao instanciar a rede virtual.", None)


class VirtNet:
    def __init__(self):
        self._net = None

    @property
    def net(self) -> Mininet | None:
        return self._net

    def generate(self) -> tuple[str, bool]:
        (err, net) = _VirtNetFactory.create()

        if err != "":
            return (err, False)

        if net is not None:
            self._net = net
            self._net.start()

        return ("", True)

    def destroy(self) -> Success | Error:
        operation_result = Success.NetworkDestructionOk

        if self._net is not None:
            try:
                self._net.stop()
                self._net = None
            except Exception:
                operation_result = Error.NetworkDestructionFailed

        Cleanup()

        return operation_result

