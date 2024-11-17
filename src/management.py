from mininet.clean import Cleanup
from typing import List

from utils import File
from data import NetworkBuilder, Policy, Error


class VirtualNetworkManager:
    def __init__(self):
        topo_schema_path = File.get_config()["topo_schema_path"]
        self.__builder = NetworkBuilder(topo_schema_path=topo_schema_path)
        self.__net = None

    def generate(self) -> bool:
        try:
            self.__net = self.__builder.build_network()
            self.__net.start()

            return True
        except Error.InvalidTopology:
            return False
        except Exception:
            return False

    def destroy(self) -> bool:
        try:
            if self.__net is not None:
                self.__net.stop()

            Cleanup()
            return True
        except Exception:
            return False

    def report_state(self) -> bool:
        return True

class FlowManager:
    def __init__(self):
        self.__config: dict = {}
        self.policies: List[Policy] = []

    def __validate(self, policy: Policy) -> bool:
        try:
            errors = []

            if not policy.name:
                errors.append("Nome de política inválido.")
            
            if not isinstance(policy.traffic_type, Policy.PolicyTypes):
                errors.append("Tipo de tráfego fornecido é inválido.")
            
            if not (0 < policy.bandwidth_reserved <= 1000):
                errors.append("Largura de banda reservada deve estar entre 1 e 100 Mbps.")

            if errors:
                return False
            
        except Exception:
            return False
        
        finally:
            print("Política validada com sucesso.")

    def __init_framework_config(self) -> bool:
        # inicializa o arquivo de config do controlador
        pass

    def __update_tables(self) -> bool:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego
        pass

    def __process_alerts(self) -> bool:
        # recebe o alerta do monitor
        # chama redirect_traffic se necessário
        pass

    def redirect_traffic(self) -> bool:
        pass

    def create(self, policy: Policy) -> bool:
        try:
            validation = self.__validate(policy)

            if not validation:
                return False
            
            self.policies.append(policy)

            update = self.__update_tables()
            
            if not update:
                self.policies.remove(policy)
                return False
            
            return True
        
        except Exception as e:
            print(f"Erro ao criar política: {e}")
            return False
        
        finally:
            print("Operação de criação de política finalizada.")

    def update(self, policy: Policy) -> bool:
        pass

    def remove(self, policy: Policy) -> bool:
        pass

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

