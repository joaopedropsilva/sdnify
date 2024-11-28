from enum import Enum
import yaml
from typing import List


class Success(Enum):
    OperationOk = "Operação bem sucedida."
    NetworkBuildOk = "Rede virtual instanciada com sucesso."
    NetworkDestructionOk = "Rede virtual destruída com sucesso."
    PolicyCreationOk = "Política de classificação criada com sucesso."
    PolicyUpdateOk = "Política de tráfego atualizada com sucesso."
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
    PolicyAlreadyExists = "A política de tráfego já existe. Operação abortada."
    BandwidthAlreadyCorrect = "A largura de banda reservada já está configurada corretamente."
    PolicyNotFound = "Política de tráfego não encontrada."
    PolicyNotFoundForDeletion = "Política de tráfego não encontrada para remoção."
    UnknownOperation = "Operação desconhecida. Use 'create', 'update' ou 'delete'."
    InvalidBandwidthValue = "A banda reservada deve ser um valor entre 1 e 100."


class PolicyTypes(Enum):
    VOIP = "voip"
    HTTP = "http"
    FTP = "ftp"

class Policy:
    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth = bandwidth


class FlowManager:
    __MIN_BANDWIDTH_RESERVED = 1
    __MAX_BANDWIDTH_RESERVED = 100
    
    def __init__(self):
        self.__config: dict = {}
        self.__policies: List[Policy] = []
        self.__meters: dict = {}


    def update_tables(self, policy: Policy, operation: str) -> Success | Error:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego

        if operation == "create":
            # Verifica se a política já existe, e caso exista, retorna aborta a operacao
            if any(p.traffic_type == policy.traffic_type for p in self.__policies):
                return Error.PolicyAlreadyExists
            
            #A partir daqui admite-se que a politica ainda nao existe e que ela apresenta
            #todos os parametros necessarios para a criacao de uma nova regra.

            # cria a estrutura de regra com base na política
            print(f"Criando banda para {policy.bandwidth}")
            rule = self.__create_rule(policy)

            # adiciona a nova política na lista de politicas
            self.__policies.append(policy)

            # confirma que o tipo da politica nao existe no dicionario de configuracao
            # e cria uma entranda com uma lista vazia que depois recebe a regra,
            #  necessario antes de reescrever o arquivo acls.yaml do faucet
            if f"{policy.traffic_type}-traffic" not in self.__config:
                self.__config[f"{policy.traffic_type}-traffic"] = []

            self.__config[f"{policy.traffic_type}-traffic"].append(rule)

            # faz a escrita no arquivo acls.yaml e retorna a mensagem confirmando 
            self.__write_config()

            return Success.PolicyCreationOk

        elif operation == "update":
            for existing_policy in self.__policies:
                if existing_policy.traffic_type == policy.traffic_type:
                    existing_policy.bandwidth = policy.bandwidth
                    rule = self.__create_rule(policy)
                    # Atualiza a configuração
                    self.__config[f"{policy.traffic_type}-traffic"] = [rule]
                    self.__write_config()
                    return Success.PolicyUpdateOk

            # caso a politica nao exista, retorna a negativa 
            return Error.PolicyNotFound

        elif operation == "delete":
            # Verifica se a política existe
            matching_policies = [p for p in self.__policies if p.traffic_type == policy.traffic_type]
            if not matching_policies:
                return Error.PolicyNotFoundForDeletion

            # Remove a política da lista
            self.__policies = [p for p in self.__policies if p.traffic_type != policy.traffic_type]
            

            # Remove da configuração
            traffic_key = f"{policy.traffic_type}-traffic"
            if traffic_key in self.__config:
                #print("esta deletando traffic key")
                del self.__config[traffic_key]

            # Remove o meter associado
            meter_name = f"qos_meter_{policy.name.lower()}"
            # print(f"Meter name to delete: {meter_name}")
            # print("Current meters:", self.__meters)
            if meter_name in self.__meters:
                #print("esta deletando meter")
                del self.__meters[meter_name]

            # print("Current config:", self.__config)
            # print("Current meters:", self.__meters)


            # Atualiza o arquivo de configuração
            result = self.__write_config()


            # Retorna o status da exclusão
            if result == Success.ConfigWriteOk:
                return Success.PolicyDeletionOk
            else:
                return Error.ConfigWriteFailure
                


    def __create_rule(self, policy: Policy):
        """
        Cria a regra de tráfego baseada na política.
        """

        meter_name, meter_config = self._create_meter(policy)
        self.__meters[meter_name] = meter_config

        # Criação de regra genérica com base no tipo de tráfego
        rule = {
            "acl_name": policy.traffic_type, 
            "rules": [
                {
                    "dl_type": "0x800",  # Endereços IPv4 (exemplo genérico)
                    "nw_proto": 17 if policy.traffic_type == PolicyTypes.VOIP else 6,  # UDP (VoIP) ou TCP (HTTP e FTP)
                    "udp_dst": 53 if policy.traffic_type == PolicyTypes.VOIP else None,  # Porta padrão UDP para VoIP
                    "tcp_dst": 80 if policy.traffic_type != PolicyTypes.VOIP else None,  # Porta padrão para HTTP/FTP
                    "actions": {
                        "allow": 1,  # Permitir
                        "meter": meter_name  # Associa o meter dinâmico
                    }
                }
            ]
        }
        return rule


    def _create_meter(self, policy: Policy) -> dict:
        """
        Cria a configuração de um meter com base na política.
        """

        # Calcula a banda reservada em Mbps e converte para bps
        reserved_bandwidth = (policy.bandwidth / 100) * 1000000 # Percentual tratado da banda reservada em bps

        meter_name = f"qos_meter_{policy.name.lower()}"

        meter_config = {
            "name": meter_name,
            "rates": [{"rate": reserved_bandwidth, "unit": "bits_per_second"}]
        }
        return meter_name, meter_config


    def generate_faucet_config(self):
        """
        Gera a configuração completa de ACLs e Meters no formato do Faucet.
        """
        acls = []
        meters = {}
        
        for policy in self.__policies:
            # Create meter
            meter_name, meter_config = self._create_meter(policy)
            meters[meter_name] = meter_config
            
            # Create ACL rule
            acl_rule = self.__create_rule(policy)
            
            # Append the ACL rule
            acls.append({
                "acl_name": policy.name,
                "rules": acl_rule["rules"]
            })
        
        # import json
        # print(json.dumps({"acls": acls, "meters": meters}, indent=2))
        return {
            "acls": acls,
            "meters": meters
        }



    def __write_config(self):
        """
        Atualiza o arquivo faucet.yaml com o conteúdo de self.__config,
        mantendo as entradas já existentes.
        """
        try:
            # Load existing configuration
            try:
                with open("faucet.yaml", "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                existing_config = {}
            
            # Generate new Faucet configuration
            new_faucet_config = self.generate_faucet_config()
            
            # Remover ACLs obsoletas (não estão na nova configuração)
            existing_config["acls"] = [
                acl for acl in existing_config.get("acls", [])
                if acl.get("acl_name") in [new_acl.get("acl_name") for new_acl in new_faucet_config.get("acls", [])]
            ]

            # Remover meters obsoletos (não estão sendo mais referenciados)
            referenced_meters = {
                rule.get("actions", {}).get("meter")
                for acl in new_faucet_config.get("acls", [])
                for rule in acl.get("rules", [])
                if rule.get("actions", {}).get("meter")
            }

            existing_config["meters"] = {
                name: config
                for name, config in existing_config.get("meters", {}).items()
                if name in referenced_meters
            }

            # Atualizar a configuração com os novos meters e ACLs
            # Atualiza os Meters
            existing_config["meters"].update(new_faucet_config.get("meters", {}))

            # Atualiza as ACLs
            if "acls" not in existing_config:
                existing_config["acls"] = []
            
            # Remover regras existentes para o mesmo nome de ACL
            existing_config["acls"] = [
                acl for acl in existing_config["acls"]
                if acl.get('acl_name') not in [new_acl.get('acl_name') for new_acl in new_faucet_config.get('acls', [])]
            ]

            # Adiciona as novas ACLs
            existing_config["acls"].extend(new_faucet_config.get("acls", []))


            # # Merge configurations
            # # Update ACLs
            # if "acls" not in existing_config:
            #     existing_config["acls"] = []
            
            # # Remove existing rules for the same traffic types
            # existing_config["acls"] = [
            #     acl for acl in existing_config["acls"] 
            #     if acl.get('acl_name') not in [new_acl.get('acl_name') for new_acl in new_faucet_config.get('acls', [])]
            # ]
            
            # # Add new ACLs
            # existing_config["acls"].extend(new_faucet_config.get('acls', []))

            # # Remove ACLs obsoletas
            # existing_config["acls"] = [
            #     acl for acl in existing_config.get("acls", [])
            #     if acl.get("acl_name") in [new_acl.get("acl_name") for new_acl in new_faucet_config.get("acls", [])]
            # ]
            
            # # Update Meters
            # existing_config["meters"] = existing_config.get("meters", {})
            # existing_config["meters"].update(new_faucet_config.get('meters', {}))
            
            # # Remove obsolete meters
            # existing_meter_names = set(existing_config["meters"].keys())
            # new_meter_names = set(new_faucet_config["meters"].keys())
            # obsolete_meters = existing_meter_names - new_meter_names
            
            # for obsolete_meter in obsolete_meters:
            #     del existing_config["meters"][obsolete_meter]

            # # Add/Update meters
            # existing_config["meters"].update(new_faucet_config.get('meters', {}))

            # Write updated configuration to faucet.yaml
            with open("faucet.yaml", "w") as file:
                yaml.dump(existing_config, file, default_flow_style=False)
            
            return Success.ConfigWriteOk
        
        except Exception as e:
            # Log the error or handle it appropriately
            return Error.ConfigWriteFailure

# Criando uma instância de FlowManager
flow_manager = FlowManager()

# Criando uma política para teste
test_policy = Policy(
    name="http_policy",
    traffic_type=PolicyTypes.HTTP,
    bandwidth=90,  
)

# Chamando o método __update_tables com a operação "create"
result_create = flow_manager.update_tables(test_policy, "create")
print(f"Create operation result: {result_create}")

# # Alterando a banda reservada para testar "update"
# test_policy_updated = Policy(
#     name="TestPolicy",
#     traffic_type=PolicyTypes.HTTP,
#     bandwidth=60,  
# )

test_policy.bandwidth = 40

result_update = flow_manager.update_tables(test_policy, "update")
print(f"Update operation result: {result_update}")

# result_create = flow_manager.update_tables(test_policy, "create")
# print(f"Create operation result: {result_create}")

test_policy_second = Policy(
    name="ftp_policy",
    traffic_type=PolicyTypes.FTP,
    bandwidth=30,  
)

test_voip = Policy(
    name="voip_policy",
    traffic_type=PolicyTypes.VOIP,
    bandwidth=15,  
)

result_create = flow_manager.update_tables(test_policy_second, "create")
print(f"Create operation result: {result_create}")

result_create = flow_manager.update_tables(test_voip, "create")
print(f"Create operation result: {result_create}")


#
#  result_delete = flow_manager.update_tables(test_policy, "delete")
# print(f"Delete operation result: {result_delete}")

# result_delete = flow_manager.update_tables(test_policy_second, "delete")
# print(f"Delete operation result: {result_delete}")
