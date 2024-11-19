from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.net import Mininet
from enum import Enum

from utils import File

class PolicyTypes(Enum):
    VOIP = 1,
    HTTP = 2,
    FTP = 3

class Warning(Enum):
    NetworkAlreadyUp = "Rede virtual já instanciada."
    NetworkUnreachable = "Rede virtual não localizada ou offline."

class Success(Enum):
    OperationOk = "Operação bem sucedida."
    NetworkBuildOk = "Rede virtual instanciada com sucesso."
    NetworkDestructionOk = "Rede virtual destruída com sucesso."
    PolicyCreationOk = "Política de classificação criada com sucesso."

class Error(Enum):
    HostsKeyWrongTypeInTopoSchema = "Chave 'hosts' deve ser do tipo list."
    HostsKeyWrongValueInTopoSchema = "Cada item da lista 'Hosts' deve ser passado como string."
    SwitchesKeyWrongTypeInTopoSchema = "Chave 'switches' deve ser do tipo 'list'."
    SwitchesKeyWrongValueInTopoSchema = "Chave 'switches' deve ser composta por uma lista de objetos."
    SwitchObjectWithNoIdInTopoSchema = "Objetos da lista 'switches' devem conter uma chave 'id' do tipo 'string'."
    SwitchObjectWithNoLinksInTopoSchema = "Objetos da lista 'switches' devem conter uma lista 'links' representando conexões."
    LinksWrongValueInTopoSchema = "Chave 'links' nos objetos da lista 'switches' deve ser do tipo string."
    NetworkBuildFailed = "Falha ao instanciar a rede virtual."
    NetworkDestructionFailed = "Falha ao destruir a rede virtual."
    InvalidPolicyTrafficType = "Tipo de tráfego inválido para política de classificação."
    InvalidPolicyBandwidth = "Largura de banda inválida para política de classificação."

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

    def __validate_topo(self,
                        schema: dict) \
                        -> Success | Error:
        if not isinstance(schema["hosts"], list):
            return Error.HostsKeyWrongTypeInTopoSchema
        
        for host in schema["hosts"]:
            if not isinstance(host, str):
                return Error.HostsKeyWrongValueInTopoSchema
        
        if not isinstance(schema["switches"], list):
            return Error.SwitchesKeyWrongTypeInTopoSchema
        
        for switch in schema["switches"]:
            if not isinstance(switch, dict):
                return Error.SwitchesKeyWrongValueInTopoSchema

            if "id" not in switch or not isinstance(switch["id"], str):
                return Error.SwitchObjectWithNoIdInTopoSchema

            if "link" not in switch or not isinstance(switch["link"], list):
                return Error.SwitchObjectWithNoLinksInTopoSchema
            
            for link in switch["link"]:
                if not isinstance(link, str):
                    return Error.LinksWrongValueInTopoSchema

        return Success.OperationOk

    def build_network(self) -> tuple[Success | Error, Mininet | None]:
        topo_schema = File.read_json_from(self.__topo_schema_path)
        validation_result = self.__validate_topo(schema=topo_schema)

        if not isinstance(validation_result, Success):
            return (validation_result, None)

        net = None
        build_result = None
        try:
            net = Mininet(topo=CustomTopo(topo_schema=topo_schema),
                          controller=self.__create_controller())
            build_result = Success.NetworkBuildOk
        except Exception:
            build_result = Error.NetworkBuildFailed

        return (build_result, net)

class Policy:
    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth = bandwidth

