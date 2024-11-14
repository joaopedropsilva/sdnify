from mininet.node import RemoteController
from mininet.topo import Topo

class Topology(Topo):
    def __init__(self, topology: dict):
        self.topology = topology

    def build(self) -> None:
        for host in self.topology["hosts"]:
            self.addHost(host)

        for switch in self.topology["switches"]:
            id = switch["id"]
            links = switch["links"]

            self.addSwitch(id)

            for host in links:
                self.addLink(host, id)

class Controller(RemoteController):
    CONTROLLER_NAME = "c0"
    CONTROLLER_ADDR = "faucet" # ver se o DNS reconhece ou preciso do IP do container
    OPF_PORT = 6653

    @staticmethod
    def create_controller(
        name: str = CONTROLLER_NAME,
        addr: str = CONTROLLER_ADDR,
        port: int = OPF_PORT
    ) -> RemoteController:
        return RemoteController(
            name,
            ip=addr,
            port=port
        )

class Validator:
    @staticmethod
    def validate_json(data: dict) -> bool:
        try:
            if not isinstance(data.get("hosts"), list):
                raise InvalidTopologyError("Chave 'Hosts' deve ser do tipo list.")
            
            for host in data["hosts"]:
                if not isinstance(host, str):
                    raise InvalidTopologyError("Cada item da lista 'Hosts' deve ser passado como string.")
            
            if not isinstance(data.get("switches"), list):
                raise InvalidTopologyError("Chave 'Switches' deve ser do tipo 'list'.")
            
            for switch in data["switches"]:
                if not isinstance(switch, dict):
                    raise InvalidTopologyError("Chave 'Switches' deve ser composta por uma lista de objetos.")
                if "id" not in switch or not isinstance(switch["id"], str):
                    raise InvalidTopologyError("Objetos da lista 'Switches' devem conter uma chave 'id' do tipo 'string'.")
                if "link" not in switch or not isinstance(switch["link"], list):
                    raise InvalidTopologyError("Objetos da lista 'Switches' devem conter uma lista 'link' representando conexões.")
                
            for link in switch["link"]:
                if not isinstance(link, str):
                    raise InvalidTopologyError("Chave 'link' nos objetos da lista 'switches' deve ser do tipo string.")

            return True

        except InvalidTopologyError as e:
            print(e)
            return False
        
        finally:
            print("Topologia Válida.")

class InvalidTopologyError(Exception):
    def __init__(self, message = "Topologia de rede inválida."):
        super().__init__(message)

