from flask import Response, jsonify, request
from mininet.net import Mininet
from typing import List
import requests

from utils import File, Api
from data import Policy


class ActionDirector:
    BASE_URL = "http://127.0.0.1:5000"  # URL do Flask Server onde a API está rodando

    @staticmethod
    def create_network(file: str) -> None:
        with open(file, 'r') as json_file:
            config_data = json_file.read()

        response = requests.post(f"{ActionDirector.BASE_URL}/start", data=config_data)

        if response.status_code == 200:
            print("Rede criada com sucesso e serviço de monitoramento inicializado.")
        else:
            print(f"Erro na criação da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def destroy_network() -> None:
        response = requests.get(f"{ActionDirector.BASE_URL}/destroy")

        if response.status_code == 200:
            print("Rede destruída com sucesso e recursos desalocados.")
        else:
            print(f"Erro na destruição da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def create_policy(name: str, protocol: str, bandwidth: float) -> None:
        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.post(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)


        if response.status_code == 200:
            print("Política criada com sucesso.")
        else:
            print(f"Erro na criação da política: Código HTTP {response.status_code} - {response.text}")


    @staticmethod
    def update_policy(name: str, protocol: str, bandwidth: float) -> None:
        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.put(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política atualizada com sucesso.")
        else:
            print(f"Erro na atualização da política: Código HTTP {response.status_code} - {response.text}")


    @staticmethod
    def remove_policy(protocol: str) -> None:
        policy_data = {"protocol": protocol}
        response = requests.delete(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política removida com sucesso.")
        else:
            print(f"Erro na remoção da política: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def show_network_state() -> None:
        response = requests.get(f"{ActionDirector.BASE_URL}/get_statistics")
        if response.status_code == 200:
            print("Informações da rede recuperadas com sucesso.")
        else:
            print(f"Erro na recuperação do estado da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def show_manual() -> None:
        pass

class ServicesController:
    def __init__(self, topology_filepath: str):
        self.__config = File.get_config()
        self.__topo_manager = TopoManager(topology_filepath=topology_filepath)
        self.__flow_manager = FlowManager()

    @Api.app.route("/start", method="POST")
    def start(self) -> Response:
        if not self.__topo_manager.generate():
            return Response(
                response="Não foi possível iniciar a rede",
                status=500
            )

        return Response(
            response="Rede iniciada com sucesso",
            status=201
        )


    @Api.app.route("/destroy")
    def destroy(self) -> Response:
        self.__topo_manager.destroy()
        return "ok"

    @Api.app.route("/get_statistics")
    def get_statistics(self) -> Response:
        return "ok"

    @Api.app.route("/manage_policy", methods=["POST", "PUT", "DELETE"])
    def manage_policy(self) -> Response:
        try:
            policy_data = request.json
            method = request.method
            
            if method == "POST":
                result = self.__flow_manager.create(policy_data)
            elif method == "PUT":
                result = self.__flow_manager.update(policy_data)
            elif method == "DELETE":
                result = self.__flow_manager.remove(policy_data)
            
            else:
                return jsonify({"error": "Método HTTP Inválido."}), 405
        
            if result.status:
                return jsonify({"status": "success", "payload": result.payload}), 200
            
            if result.status:
                return jsonify({"status": "failure", "payload": result.err_reason}), 400

        except KeyError as e:
            return jsonify({"error": "Dados Inválidos ou Incompletos.", "details": str(e)}), 500

        except Exception as e:
            return jsonify({"error": "Erro no Servidor.", "details": str(e)}), 500
        
    @Api.app.route("/capture_alerts")
    def capture_alerts(self, policy_data: dict) -> Response:
        return "ok"

class TopoManager:
    def __init__(self, topology_filepath: str):
        self.__net: Mininet = None
        self.__topology_filepath = topology_filepath

    def __load_network(self) -> tuple[bool, dict]:
        topo = Utils.read_json_from(self.__topology_filepath)
        is_topo_valid = Validator.validate_json(topo)

        return (is_topo_valid, topo if is_topo_valid else {})

    def generate(self) -> bool:
        (loaded_successfully, topology) = self.__load_network()

        if not loaded_successfully:
            return False

        self.__net = Mininet(
            topo=Topology(topology=topology),
            controller=Controller.create_controller()
        )

        self.__net.start()

        return True

    def destroy(self) -> bool:
        return True

    def report_topology_state(self) -> bool:
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

