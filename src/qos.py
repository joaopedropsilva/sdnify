from typing import List

from information import PolicyTypes, RoutineResults

class Policy:
    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth_reserved: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth_reserved = bandwidth_reserved

class FlowManager:
    def __init__(self):
        self.__config: dict = {}
        self.policies: List[Policy] = []

    def __validate(self, policy: Policy) -> RoutineResults:
        try:
            errors = []

            if not policy.name:
                errors.append("Nome de política inválido.")
            
            if not isinstance(policy.traffic_type, PolicyTypes):
                errors.append("Tipo de tráfego fornecido é inválido.")
            
            if not (0 < policy.bandwidth_reserved <= 1000):
                errors.append("Largura de banda reservada deve estar entre 1 e 100 Mbps.")

            if errors:
                return RoutineResults(status=False, err_reason="; ".join(errors))
            
        except Exception as e:
            return RoutineResults(status=False, err_reason="Erro de validação: {str(e)}")
        
        finally:
            print("Política validada com sucesso.")

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
        try:
            validation = self.__validate(policy)

            if not validation.status == False:
                return validation
            
            self.policies.append(policy)

            update = self.__update_tables()
            
            if update.status == False:
                self.policies.remove(policy)
                return update
            
            return RoutineResults(status=True, payload="Política criada com sucesso.")
        
        except Exception as e:
            print(f"Erro ao criar política: {e}")
            return RoutineResults(status=False, err_reason=str(e))
        
        finally:
            print("Operação de criação de política finalizada.")

    def update(self, policy: Policy) -> RoutineResults:
        pass

    def remove(self, policy: Policy) -> RoutineResults:
        pass


