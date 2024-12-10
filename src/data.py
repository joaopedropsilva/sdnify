from enum import Enum


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
    BandwidthNotFound = "Largura de banda inválida ausente."
    PolicyNotFound = "Política de tráfego não encontrada."
    UnknownOperation = "Operação desconhecida. Use 'create', 'update' ou 'delete'."
    InvalidBandwidthValue = "A banda reservada deve ser um valor entre 1 e 100."
    ConfigWriteFailure = "Falha ao escrever o arquivo de configuração."
    ControllerConfigNotFound = "Configuração do controlador não encontrada."

