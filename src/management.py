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
        self._config: dict = {}
        self._policies: List[Policy] = []

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
            if any(p.traffic_type == policy.traffic_type for p in self.policies):
                return Error.PolicyAlreadyExists
            
            #A partir daqui admite-se que a politica ainda nao existe e que ela apresenta
            #todos os parametros necessarios para a criacao de uma nova regra.

            # cria a estrutura de regra com base na política
            rule = self._create_rule(policy)

            # adiciona a nova política na lista de politicas
            self.policies.append(policy)

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
            policy_exists = any(p.traffic_type == policy.traffic_type for p in self.policies)

            if not policy_exists:
                return Error.PolicyNotFoundForDeletion

            # Remove a política da lista de políticas
            self.policies = [p for p in self.policies if p.traffic_type != policy.traffic_type]

            # Verifica e remove a política do dicionário de configuração, se existir
            if f"{policy.traffic_type}-traffic" in self._config:
                del self._config[f"{policy.traffic_type}-traffic"]

            # Atualiza o arquivo acls.yaml com a configuração modificada
            self._write_config()

            return Success.PolicyDeletionOk

        else:
            return Error.UnknownOperation
        

    def _create_rule(self, policy: Policy):
        """
        Cria a regra de tráfego baseada na política.
        """
        # Define a banda total disponível (exemplo: 1000 Mbps)
        total_bandwidth = 1000  # Exemplo de valor fixo. Isso pode vir de uma configuração ou ser dinâmico

        # Validação da banda reservada entre 1% e 100%
        if not (1 <= policy.bandwidth_reserved <= 100):
            return Error.InvalidBandwidthValue

        # Calcula a banda reservada em Mbps e converte para bps
        reserved_bandwidth = (policy.bandwidth_reserved / 100) * total_bandwidth * 1000000

        # Criação de regra genérica com base no tipo de tráfego
        rule = {
            "acl_name": policy.name,  # Nome da política (como acl_name no formato do Faucet)
            "rules": [
                {
                    "dl_type": "0x800",  # Endereços IPv4 (exemplo genérico)
                    "nw_proto": 17 if policy.traffic_type == PolicyTypes.VOIP else 6,  # UDP (VoIP) ou TCP (HTTP e FTP)
                    "udp_dst": 53 if policy.traffic_type == PolicyTypes.VOIP else None,  # Porta padrão UDP para VoIP
                    "tcp_dst": 80 if policy.traffic_type != PolicyTypes.VOIP else None,  # Porta padrão para HTTP/FTP
                    "actions": {
                        "allow": 1,  # Permitir
                        "set_fields": [
                            {"bandwidth_reserved": reserved_bandwidth},  # Percentual tratado da banda reservada em bps
                        ]
                    }
                }
            ]
        }


        return rule


    def _write_config(self):
        
        """
        Atualiza o arquivo acls.yaml com o conteúdo de self._config,
        mantendo as entradas já existentes.
        Retorna um objeto Error ou Success com o status da operação.
        """

        try:
            # Primeiro, carrega o conteúdo atual do arquivo acls.yaml
            try:
                with open("acls.yaml", "r") as file:
                    existing_config = yaml.safe_load(file) or {}
            except FileNotFoundError:
                # Se o arquivo não for encontrado, inicializa um dicionário vazio
                existing_config = {}

            # Atualiza o dicionário de configuração com as entradas existentes
            existing_config.update(self._config)

            # Escreve o dicionário atualizado no arquivo acls.yaml
            with open("acls.yaml", "w") as file:
                yaml.dump(existing_config, file, default_flow_style=False)

            # Retorna um sucesso com a mensagem
            return Success.ConfigWriteOk

        except Exception as e:
            # Retorna erro com a mensagem de exceção
            return Error.ConfigWriteFailure


    def _process_alerts(self) -> RoutineResults:
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

