from mininet.node import RemoteController
from mininet.topo import Topo
from enum import Enum


class Topology(Topo):
    __CONTROLLER_NAME = "c0"
    __CONTROLLER_ADDR = "faucet"
    __OPF_PORT = 6653

    def __init__(self, topology: dict, controller: RemoteController):
        self.__topology = topology
        self.__controller = controller

    @classmethod
    def create_controller(cls,
                          name: str = "",
                          addr: str = "",
                          port: int = 0) -> RemoteController:
        return RemoteController(
            name=name if name != "" else cls.__CONTROLLER_NAME,
            ip=addr if addr != "" else cls.__CONTROLLER_ADDR,
            port=port if port != 0 else cls.__OPF_PORT
        )

    def build(self) -> None:
        for host in self.__topology["hosts"]:
            self.addHost(host)

        for switch in self.__topology["switches"]:
            id = switch["id"]
            links = switch["links"]

            self.addSwitch(id)

            for host in links:
                self.addLink(host, id)

    def validate(self) -> bool:
        try:
            if not isinstance(self.__topology.get("hosts"), list):
                raise Error.InvalidTopology("Chave 'Hosts' deve ser do tipo list.")
            
            for host in self.__topology["hosts"]:
                if not isinstance(host, str):
                    raise Error.InvalidTopology("Cada item da lista 'Hosts' deve ser passado como string.")
            
            if not isinstance(self.__topology.get("switches"), list):
                raise Error.InvalidTopology("Chave 'Switches' deve ser do tipo 'list'.")
            
            for switch in self.__topology["switches"]:
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

