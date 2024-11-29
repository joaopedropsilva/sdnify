from mininet.node import RemoteController
from mininet.topo import Topo
from mininet.net import Mininet
from enum import Enum

from src.utils import File

class PolicyTypes(Enum):
    VOIP = "voip"
    HTTP = "http"
    FTP = "ftp"

class Warning(Enum):
    NetworkAlreadyUp = "Rede virtual já instanciada."
    NetworkUnreachable = "Rede virtual não localizada ou offline."

class Success(Enum):
    OperationOk = "Operação bem sucedida."
    NetworkBuildOk = "Rede virtual instanciada com sucesso."
    NetworkDestructionOk = "Rede virtual destruída com sucesso."
    PolicyCreationOk = "Política de classificação criada com sucesso."
    PolicyDeletionOk = "Política de tráfego removida com sucesso."
    ConfigWriteOk = "Configuração escrita no arquivo acls.yaml com sucesso."

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
    PolicyNotFound = "Política de tráfego não encontrada."
    UnknownOperation = "Operação desconhecida. Use 'create', 'update' ou 'delete'."
    InvalidBandwidthValue = "A banda reservada deve ser um valor entre 1 e 100."
    ConfigWriteFailure = "Falha ao escrever o arquivo de configuração."

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
    _DEFAULT_CONTROLLER_NAME = "c0"
    _DEFAULT_CONTROLLER_IP = "faucet"
    _DEFAULT_OPF_PORT = 6653

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
        hosts_key = "hosts"
        switches_key = "switches"
        id_key = "id"
        links_key = "links"

        if not isinstance(schema[hosts_key], list):
            return Error.HostsKeyWrongTypeInTopoSchema
        
        for host in schema[hosts_key]:
            if not isinstance(host, str):
                return Error.HostsKeyWrongValueInTopoSchema
        
        if not isinstance(schema[switches_key], list):
            return Error.SwitchesKeyWrongTypeInTopoSchema
        
        for switch in schema[switches_key]:
            if not isinstance(switch, dict):
                return Error.SwitchesKeyWrongValueInTopoSchema

            if id_key not in switch or not isinstance(switch[id_key], str):
                return Error.SwitchObjectWithNoIdInTopoSchema

            if links_key not in switch or not isinstance(switch[links_key], list):
                return Error.SwitchObjectWithNoLinksInTopoSchema
            
            for link in switch[links_key]:
                if not isinstance(link, str):
                    return Error.LinksWrongValueInTopoSchema

        return Success.OperationOk

    def build_network(self) -> tuple[Success | Error, Mininet | None]:
        topo_schema = File.read_json_from(self._topo_schema_path)
        validation_result = self._validate_topo(schema=topo_schema)

        if not isinstance(validation_result, Success):
            return (validation_result, None)

        net = None
        build_result = None
        try:
            net = Mininet(topo=CustomTopo(topo_schema=topo_schema),
                          controller=self._create_controller())
            build_result = Success.NetworkBuildOk
        except Exception:
            build_result = Error.NetworkBuildFailed

        return (build_result, net)

class Policy:
    def __init__(self, traffic_type: PolicyTypes, bandwidth: int):
        self.traffic_type = traffic_type
        self.bandwidth = bandwidth

