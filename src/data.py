from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.net import Mininet
from enum import Enum

from utils import File

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

class NetworkBuilder():
    __DEFAULT_CONTROLLER_NAME = "c0"
    __DEFAULT_CONTROLLER_ADDR = "faucet"
    __DEFAULT_OPF_PORT = 6653

    def __init__(self, topo_schema_path: str, controller_options: dict = {}):
        self.__topo_schema_path = topo_schema_path
        self.__topo = None
        self.__controller_name = controller_options["name"] \
                                    if len(controller_options) \
                                    else self.__DEFAULT_CONTROLLER_NAME
        self.__controller_addr = controller_options["addr"] \
                                    if len(controller_options) \
                                    else self.__DEFAULT_CONTROLLER_ADDR
        self.__opf_port = controller_options["opf_port"] \
                                    if len(controller_options) \
                                    else self.__DEFAULT_OPF_PORT

    def __create_controller(self) -> RemoteController:
        return RemoteController(
            name=self.__controller_name,
            addr=self.__controller_addr,
            port=self.__opf_port
        )

    def __validate_topo(self, schema: dict) -> bool:
        try:
            if not isinstance(schema.get("hosts"), list):
                raise Error.InvalidTopology("Chave 'Hosts' deve ser do tipo list.")
            
            for host in schema["hosts"]:
                if not isinstance(host, str):
                    raise Error.InvalidTopology("Cada item da lista 'Hosts' deve ser passado como string.")
            
            if not isinstance(schema.get("switches"), list):
                raise Error.InvalidTopology("Chave 'Switches' deve ser do tipo 'list'.")
            
            for switch in schema["switches"]:
                if not isinstance(switch, dict):
                    raise Error.InvalidTopology("Chave 'Switches' deve ser composta por uma lista de objetos.")
                if "id" not in switch or not isinstance(switch["id"], str):
                    raise Error.InvalidTopology("Objetos da lista 'Switches' devem conter uma chave 'id' do tipo 'string'.")
                if "link" not in switch or not isinstance(switch["link"], list):
                    raise Error.InvalidTopology("Objetos da lista 'Switches' devem conter uma lista 'link' representando conexões.")
                
            for link in switch["link"]:
                if not isinstance(link, str):
                    raise Error.InvalidTopology("Chave 'link' nos objetos da lista 'switches' deve ser do tipo string.")

            return True

        except Error.InvalidTopology as e:
            print(e)
            return False
        
        finally:
            print("Topologia Válida.")

    def __build_topo(self):
        topo_schema = File.read_json_from(self.__topo_schema_path)
        is_topo_valid = self.__validate_topo(schema=topo_schema)

        if not is_topo_valid:
            raise Error.InvalidTopology()

        self.__topo = CustomTopo(topo_schema=topo_schema)

    def build_network(self) -> Mininet:
        self.__build_topo()

        return Mininet(
            topo=self.__topo,
            controller=self.__create_controller()
        )

class Policy:
    class PolicyTypes(Enum):
        VOIP = 1,
        HTTP = 2,
        FTP = 3

    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth_reserved: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth_reserved = bandwidth_reserved

class Error:
    class InvalidTopology(Exception):
        def __init__(self, message: str = "Topologia de rede inválida."):
            super().__init__(message)

