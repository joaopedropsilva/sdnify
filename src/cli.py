from argparse import ArgumentParser
from subprocess import run
#import requests


# Padronizar output em STDOUT
class Actions:
    _API_URL = "http://127.0.0.1:5000"

    @classmethod
    def create_network(cls) -> None:
        response = requests.post(f"{cls._API_URL}/virtnet/start")

        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def destroy_network(cls) -> None:
        response = requests.get(f"{cls._API_URL}/virtnet/destroy")

        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def create_policy(cls, traffic_type: str, bandwidth: float) -> None:
        policy = {"traffic_type": traffic_type, "bandwidth": bandwidth}
        response = requests.post(f"{cls._API_URL}/manage_policy", json=policy)

        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def remove_policy(cls, traffic_type: str) -> None:
        policy = {"traffic_type": traffic_type}
        response = requests.delete(f"{cls._API_URL}/manage_policy", json=policy)
        
        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def show_network_state(cls) -> None:
        response = requests.get(f"{cls._API_URL}/virtnet/status")

        print(f"STATUS: {response.status_code} - {response.text}")

    @staticmethod
    def show_manual() -> None:
        pass

    @staticmethod
    def run_tests(interactive: bool, test_file: str) -> None:
        script = []

        if interactive:
            script = ["python", "-m", "tests.interactive"]

        if test_file is not None:
            script = ["python", "-m", f"tests.{test_file}"]

        # Ctrl + C ainda para esse processo
        run(script)


class Dispatcher:
    @staticmethod
    def _create_arg_parser() -> ArgumentParser:
        parser = ArgumentParser(description="SDNify: Gerenciador de Redes SDN")

        parser.add_argument(
            "action",
            type=str,
            choices=["create_network",
                     "destroy_network",
                     "create_policy",
                     "remove_policy",
                     "show_network_state",
                     "show_manual",
                     "test"],
            help="Escolha a ação a ser executada"
        )

        parser.add_argument("--traffic-type",
                            type=str,
                            help="Tipo de tráfego alvo da política \
                                (ex: HTTP, FTP e VOiP)")

        parser.add_argument("--bandwidth",
                            type=float,
                            help="Largura de banda para a política")

        parser.add_argument("--interactive",
                            "-i",
                            action="store_true",
                            help="Executar testes no modo interativo")

        parser.add_argument("--file",
                            "-f",
                            type=str,
                            help="Nome do arquivo de testes a executar")
        return parser
    
    @classmethod
    def dispatch(cls):
        parser = cls._create_arg_parser()

        args = parser.parse_args()
        action_map = {
            "create_network": Actions.create_network,
            "destroy_network": Actions.destroy_network,
            "create_policy": lambda: Actions.create_policy(args.traffic_type,
                                                           args.bandwidth),
            "remove_policy": lambda: Actions.remove_policy(args.traffic_type),
            "show_network_state": Actions.show_network_state,
            "show_manual": Actions.show_manual,
            "test": lambda: Actions.run_tests(args.interactive,
                                                   args.file)
        }

        if args.action in action_map:
            action_map[args.action]()
        else:
            print("Ação desconhecida. Use --help para ver as opções.")

if __name__ == "__main__":
    Dispatcher.dispatch()

