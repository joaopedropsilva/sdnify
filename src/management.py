from mininet.clean import Cleanup
from typing import List

from utils import File
from data import NetworkBuilder, Policy, PolicyTypes, Success, Error


class VirtualNetworkManager:
    def __init__(self):
        topo_schema_path = File.get_config()["topo_schema_path"]
        self.__builder = NetworkBuilder(topo_schema_path=topo_schema_path)
        self.__net = None

    def generate(self) -> Success | Error:
        (build_result, net) = self.__builder.build_network()

        if isinstance(build_result, Success):
            if net is not None:
                self.__net = net
                self.__net.start()

        return build_result

    def destroy(self) -> Success | Error:
        operation_result = Success.NetworkDestructionOk

        if self.__net is not None:
            try:
                self.__net.stop()
            except Exception:
                operation_result = Error.NetworkDestructionFailed

        Cleanup()

        return operation_result

    def report_state(self) -> None:
        pass

class FlowManager:
    __MIN_BANDWIDTH_RESERVED = 1
    __MAX_BANDWIDTH_RESERVED = 100

    def __init__(self):
        self.__config: dict = {}
        self.__policies: List[Policy] = []

    def __validate(self, policy: Policy) -> Success | Error:
        # Remover
        if policy.name == "":
            return Error.InvalidPolicyTrafficType
        
        if not isinstance(policy.traffic_type, PolicyTypes):
            return Error.InvalidPolicyTrafficType
        
        if not (policy.bandwidth < self.__MIN_BANDWIDTH_RESERVED
                and policy.bandwidth > self.__MAX_BANDWIDTH_RESERVED):
            return Error.InvalidPolicyBandwidth

        return Success.OperationOk

    def __init_framework_config(self) -> bool:
        # inicializa o arquivo de config do controlador
        return False

    def __update_tables(self) -> Success | Error:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego
        return Success.OperationOk

    def __process_alerts(self) -> bool:
        # recebe o alerta do monitor
        # chama redirect_traffic se necessário
        return False

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        validation_result = self.__validate(policy)
        if isinstance(validation_result, Error):
            return validation_result
        
        self.__policies.append(policy)

        tables_update_result = self.__update_tables()
        if isinstance(tables_update_result, Error):
            self.__policies.remove(policy)
            return tables_update_result
        
        return Success.PolicyCreationOk

    def update(self, policy: Policy) -> Success | Error:
        try:
            validation = self.__validate(policy)
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
            validation = self.__validate(policy)
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
        self.__virtual_network = VirtualNetworkManager()
        self.__flow = FlowManager()
        self.__is_network_alive = False

    @property
    def virtual_network(self) -> VirtualNetworkManager:
        return self.__virtual_network

    @property
    def flow(self) -> FlowManager:
        return self.__flow

    @property
    def is_network_alive(self) -> bool:
        return self.__is_network_alive

    @is_network_alive.setter
    def is_network_alive(self, network_status: bool) -> None:
        self.__is_network_alive = network_status

