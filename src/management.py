from mininet.clean import Cleanup
from typing import List
import yaml

from src.utils import File
from src.data import NetworkBuilder, Policy, PolicyTypes, Success, Error


class VirtualNetworkManager:
    def __init__(self):
        topo_schema_path = File.get_config()["topo_schema_path"]
        self._builder = NetworkBuilder(topo_schema_path=topo_schema_path)
        self._net = None

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

    def report_state(self) -> None:
        pass

class FlowManager:
    _MIN_BANDWIDTH_RESERVED = 1
    _MAX_BANDWIDTH_RESERVED = 100
    
    def __init__(self):
        self.__config: dict = {}
        self.__policies: List[Policy] = []
        self.__meters: dict = {}

    def _validate(self, policy: Policy) -> Success | Error:
        # Remover
        if policy.name == "":
            return Error.InvalidPolicyTrafficType
        
        if not isinstance(policy.traffic_type, PolicyTypes):
            return Error.InvalidPolicyTrafficType
        
        if not (policy.bandwidth < self._MIN_BANDWIDTH_RESERVED
                and policy.bandwidth > self._MAX_BANDWIDTH_RESERVED):
            return Error.InvalidPolicyBandwidth

        return Success.OperationOk

    def _init_framework_config(self) -> bool:
        # inicializa o arquivo de config do controlador
        return False

    def _update_tables(self, policy: Policy, operation: str) -> Success | Error:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego

        if operation == "create":
            # Verifica se a política já existe, e caso exista, retorna aborta a operacao
            if any(p.traffic_type == policy.traffic_type for p in self.__policies):
                return Error.PolicyAlreadyExists
            
            #A partir daqui admite-se que a politica ainda nao existe e que ela apresenta
            #todos os parametros necessarios para a criacao de uma nova regra.

            # cria a estrutura de regra com base na política
            rule = self._create_rule(policy)

            # adiciona a nova política na lista de politicas
            self.__policies.append(policy)

            # confirma que o tipo da politica nao existe no dicionario de configuracao
            # e cria uma entranda com uma lista vazia que depois recebe a regra,
            #  necessario antes de reescrever o arquivo acls.yaml do faucet
            if f"{policy.traffic_type}-traffic" not in self._config:
                self._config[f"{policy.traffic_type}-traffic"] = []

            self._config[f"{policy.traffic_type}-traffic"].append(rule)

            # faz a escrita no arquivo acls.yaml e retorna a mensagem confirmando 
            self._write_config()

            return Success.PolicyCreationOk

        elif operation == "update":
            for existing_policy in self.policies:
                if existing_policy.traffic_type == policy.traffic_type:
                    # Só modifica a banda se ela for diferente da atual
                    if existing_policy.bandwidth_reserved != policy.bandwidth_reserved:
                        existing_policy.bandwidth_reserved = policy.bandwidth_reserved
                        rule = self._create_rule(policy)
                        # Atualiza a configuração
                        self._config[f"{policy.traffic_type}-traffic"] = [rule]
                        self._write_config()
                        return Success.PolicyUpdateOk
                    else:
                        # Se a banda não mudou, não faz nada
                        return Error.BandwidthAlreadyCorrect

            # caso a politica nao exista, retorna a negativa 
            return Error.PolicyNotFound

        elif operation == "delete":
            # Verifica se a política existe na lista de políticas
            if not any(p.traffic_type == policy.traffic_type for p in self.__policies):
                    return Error.PolicyNotFoundForDeletion

            # Remove a política da lista e dicionário de políticas junto ao limite de banda se existir 
            self.__policies = [p for p in self.__policies if p.traffic_type != policy.traffic_type]
            if f"{policy.traffic_type}-traffic" in self.__config:
                del self.__config[f"{policy.traffic_type}-traffic"]

            meter_name = f"qos_meter_{policy.name.lower()}"
            if meter_name in self.__meters:
                del self.__meters[meter_name]

            # Atualiza o arquivo acls.yaml com a configuração modificada
            self.__write_config()
            return Success.PolicyDeletionOk

        else:
            return Error.UnknownOperation
        

    def _create_rule(self, policy: Policy):
        """
        Cria a regra de tráfego baseada na política.
        """

        meter_name, meter_config = self._create_meter(policy)
        self.__meters[meter_name] = meter_config

        # Criação de regra genérica com base no tipo de tráfego
        rule = {
            "acl_name": policy.traffic_type,  # Nome da política (como acl_name no formato do Faucet)
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
        reserved_bandwidth = (policy.bandwidth / 100) * self._MAX_BANDWIDTH * 1000000 # Percentual tratado da banda reservada em bps

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
        
        return {
            "acls": acls,
            "meters": meters
        }

    def _write_config(self):
        
        """
        Atualiza o arquivo faucet.yaml com o conteúdo de self.__config,
        mantendo as entradas já existentes.
        """
        try:
            faucet_config = self.generate_faucet_config()
            
            try:
                with open("faucet.yaml", "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                existing_config = {}
            
            faucet_yaml_config = {
                "acls": faucet_config.get("acls", []),
                "meters": faucet_config.get("meters", {})
            }
            
            existing_config.update(faucet_yaml_config)
            
            with open("faucet.yaml", "w") as file:
                yaml.dump(existing_config, file, default_flow_style=False)
            
            return Success.ConfigWriteOk
        
        except Exception as e:
            return Error.ConfigWriteFailure

    def __process_alerts(self) -> RoutineResults:
        # recebe o alerta do monitor
        # chama redirect_traffic se necessário
        return False

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        validation_result = self._validate(policy)
        if isinstance(validation_result, Error):
            return validation_result
        
        self._policies.append(policy)

        tables_update_result = self._update_tables()
        if isinstance(tables_update_result, Error):
            self._policies.remove(policy)
            return tables_update_result
        
        return Success.PolicyCreationOk

    def update(self, policy: Policy) -> Success | Error:
        try:
            validation = self._validate(policy)
            if validation.status == False:
                return RoutineResults(status=False, err_reason="Falha na validação da política: " + validation.err_reason)

            existing_policy = next((p for p in self.policies if p.name == policy.name), None)
            if not existing_policy:
                return RoutineResults(status=False, err_reason="Política não encontrada.")
            
            existing_policy.traffic_type = policy.traffic_type
            existing_policy.bandwidth_reserved = policy.bandwidth_reserved

            return RoutineResults(status=True, payload="Política atualizada com sucesso.")
        
        except Exception as e:
            return RoutineResults(status=False, err_reason="Falha ao atualizar política: str{e}")
        
        finally:
            print("Operação de atualização de políticas finalizado.")

    def remove(self, policy: Policy) -> Success | Error:
        try:
            validation = self._validate(policy)
            if validation.status == False:
                return RoutineResults(status=False, err_reason="Falha na validação da política: " + validation.err_reason)

            existing_policy = next((p for p in self.policies if p.name == policy.name), None)
            if not existing_policy:
                return RoutineResults(status=False, err_reason="Política não encontrada.")
            
            self.policies.remove(existing_policy)

            return RoutineResults(status=True, payload="Política removida com sucesso.")
        
        except Exception as e:
            return RoutineResults(status=False, err_reason="Falha ao remover política: str{e}")
        
        finally:
            print("Operação de remoção de políticas finalizado.")

class Managers:
    def __init__(self):
        self._virtual_network = VirtualNetworkManager()
        self._flow = FlowManager()
        self._is_network_alive = False

    @property
    def virtual_network(self) -> VirtualNetworkManager:
        return self._virtual_network

    @property
    def flow(self) -> FlowManager:
        return self._flow

    @property
    def is_network_alive(self) -> bool:
        return self._is_network_alive

    @is_network_alive.setter
    def is_network_alive(self, network_status: bool) -> None:
        self._is_network_alive = network_status

