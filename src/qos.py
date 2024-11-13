from typing import List

from information import PolicyTypes, RoutineResults

class FlowManager:
    def __init__(self):
        self.__config: dict = {}
        self.policies: List[Policy] = []

    def __validate(self, policy: Policy) -> RoutineResults:
        pass

    def __init_framework_config(self) -> RoutineResults:
        # inicializa o arquivo de config do controlador
        pass

    def __update_tables(self) -> RoutineResults:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego
        pass

    def __process_alerts(self) -> RoutineResults:
        # recebe o alerta do monitor
        # chama redirect_traffic se necessário
        pass

    def redirect_traffic(self) -> RoutineResults:
        pass

    def create(self, policy: Policy) -> RoutineResults:
        pass

    def update(self, policy: Policy) -> RoutineResults:
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

    def remove(self, policy: Policy) -> RoutineResults:
        pass

class Policy:
    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth_reserved: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth_reserved = bandwidth_reserved

