from flask import Flask, Response
from mininet.node import RemoteController
from mininet.topo import Topo
from typing import List

from qos import FlowManager
from monitor import MonitorService
from information import RoutineResults, Display, Manual

import requests

class ActionDirector:
    @staticmethod
    def __read_args() -> dict:
        pass

    BASE_URL = "http://127.0.0.1:5000"  # URL do Flask Server onde a API está rodando

    @staticmethod
    def create_network(file: str) -> None:
        """
            Inicializa um controlador de serviços num novo processo
        """
        with open(file, 'r') as json_file:
            config_data = json_file.read()

        response = requests.post(f"{ActionDirector.BASE_URL}/start", data=config_data)

        if response.status_code == 200:
            print("Rede criada com sucesso e serviço de monitoramento inicializado.")
        else:
            print(f"Erro na criação da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def destroy_network() -> None:
        """
            Executa as rotinas para a destruição da rede criada.
        """

        response = requests.get(f"{ActionDirector.BASE_URL}/destroy")

        if response.status_code == 200:
            print("Rede destruída com sucesso e recursos desalocados.")
        else:
            print(f"Erro na destruição da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def create_policy(name: str, protocol: str, bandwidth: float) -> None:
        """
            Recebe as informações da política por parâmetros CLI
            e executa as rotinas de criação de uma nova política.
        """

        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.post(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)


        if response.status_code == 200:
            print("Política criada com sucesso.")
        else:
            print(f"Erro na criação da política: Código HTTP {response.status_code} - {response.text}")


    @staticmethod
    def update_policy(name: str, protocol: str, bandwidth: float) -> None:
        """
            Recebe as informações da política por parâmetros CLI
            e executa as rotinas de atualização de políticas.
        """
        
        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.put(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política atualizada com sucesso.")
        else:
            print(f"Erro na atualização da política: Código HTTP {response.status_code} - {response.text}")


    @staticmethod
    def remove_policy(protocol: str) -> None:
        """
            Recebe as informações da política por parâmetros CLI
            e executa as rotinas de remoção de políticas.
        """
        
        policy_data = {"protocol": protocol}
        response = requests.delete(f"{ActionDirector.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política removida com sucesso.")
        else:
            print(f"Erro na remoção da política: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def show_network_state() -> None:
        """
            Executa rotinas de recuperação de informações sobre
            a rede instanciada, as políticas ativas e o monitoramento
        """
        
        response = requests.get(f"{ActionDirector.BASE_URL}/get_statistics")
        if response.status_code == 200:
            print("Informações da rede recuperadas com sucesso.")
        else:
            print(f"Erro na recuperação do estado da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def show_manual() -> None:
        """
            Exibe informações do manual do controlador com um nível de
            detalhes a depender do especificado por parâmetros CLI.
        """
        pass

class Api:
    app = Flask(__name__)

class ServicesController:
    def __init__(self):
        self.__config = None # read_config
        self.__topo_manager = TopoManager()
        self.__flow_manager = FlowManager()
        self.__monitor_service = MonitorService()

    @Api.app.route("/start")
    def start(self) -> str:
        """
            Inicializa o editor de topologia e gera a topologia desejada,
            se houver sucesso na geração inicializa o serviço de monitoramento.
        """
        return "ok"

    @Api.app.route("/destroy")
    def destroy(self) -> Response:
        """
            Executa a rotina de desalocação de recursos da rede.
        """
        self.__topo_manager.destroy()
        return "ok"

    @Api.app.route("/get_statistics")
    def get_statistics(self) -> Response:
        """
            Executa a rotina de recuperação de informações da rede.
        """
        return "ok"

    @Api.app.route("/manage_policy")
    def manage_policy(self) -> Response:
        
        return "ok"

    @Api.app.route("/capture_alerts")
    def capture_alerts(self, policy_data: dict) -> Response:
        
        return "ok"

class TopoManager:
    def __init__(self):
        self.__net: Mininet = None

    def __load_network(self) -> RoutineResults:
        """
            Procura pelo arquivo JSON de topologia definida no diretório ASSETS_DIR,
            interpreta cada valor no arquivo e inicializa o gerenciador de topologia.
        """
        topo = Topology()
        controller = Controller.create_controller()
        self.__net = Mininet(topo, controller)

    def generate(self) -> RoutineResults:
        """
            Carrega a topologia desejada.
        """
        psr = self.__load_network()

        if not psr.status:
            # retorna PSR com erro
            pass 

        self.__net.start()

    def destroy(self) -> RoutineResults:
        """
            Desaloca os recursos da topologia instanciada.
        """
        pass

    def report_topology_state(self) -> RoutineResults:
        """
            Recupera informações sobre a topologia instanciada.
        """
        pass

class Topology(Topo):
    def build(self) -> None:
        pass

class Controller(RemoteController):
    CONTROLLER_NAME = "c0"
    CONTROLLER_ADDR = "127.0.0.1"
    OPF_PORT = 6653

    @staticmethod
    def create_controller(
        name: str = CONTROLLER_NAME,
        addr: str = CONTROLLER_ADDR,
        port: int = OPF_PORT
    ) -> RemoteController:
        return RemoteController(
            name,
            ip=addr,
            port=port
        )

