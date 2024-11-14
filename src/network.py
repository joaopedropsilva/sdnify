from flask import Flask, Response
from mininet.net import Mininet

from qos import FlowManager
from information import Utils
from topo import Validator, Topology, Controller


class ActionDirector:
    @staticmethod
    def create_network() -> None:
        pass

    @staticmethod
    def destroy_network() -> None:
        pass

    @staticmethod
    def create_policy() -> None:
        pass

    @staticmethod
    def update_policy() -> None:
        pass

    @staticmethod
    def remove_policy() -> None:
        pass

    @staticmethod
    def show_network_state() -> None:
        pass

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
        pass

    @Api.app.route("/get_statistics")
    def get_statistics(self) -> Response:
        pass

    @Api.app.route("/manage_policy")
    def manage_policy(self) -> Response:
        pass

    @Api.app.route("/capture_alerts")
    def capture_alerts(self, policy_data: dict) -> Response:
        pass

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

