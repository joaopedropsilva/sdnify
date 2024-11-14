from flask import Flask, Response
from mininet.net import Mininet
import requests

from qos import FlowManager
from information import Utils
from topo import Validator, Topology, Controller


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

class Api:
    app = Flask(__name__)

class ServicesController:
    def __init__(self, topology_filepath: str):
        self.__config = Utils.read_json_from() # ler do caminho do projeto
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

    @Api.app.route("/manage_policy")
    def manage_policy(self) -> Response:
        return "ok"

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

