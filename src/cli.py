from argparse import ArgumentParser
from flask import Response
from subprocess import run
import requests

from src.utils import Manual


class _Actions:
    _API_URL = "http://127.0.0.1:5000"

    @staticmethod
    def _format_api_output_to_stdout(func):
        def _wrapper(_cls, *args):
            response = func(_cls, *args)

            print(f"[cli] {response.status_code} | {response.text}")


        return _wrapper

    @classmethod
    @_format_api_output_to_stdout
    def virtnet_create(cls) -> Response:
        return requests.post(f"{cls._API_URL}/virtnet/create")

    @classmethod
    @_format_api_output_to_stdout
    def virtnet_destroy(cls) -> Response:
        return requests.post(f"{cls._API_URL}/virtnet/destroy")

    @classmethod
    @_format_api_output_to_stdout
    def virtnet_status(cls) -> Response:
        return requests.get(f"{cls._API_URL}/virtnet/status")

    @classmethod
    @_format_api_output_to_stdout
    def create_policy(cls, traffic_type: str, bandwidth: int) -> Response:
       data = {"traffic_type": traffic_type, "bandwidth": bandwidth}
       return requests.post(f"{cls._API_URL}/manager/manage_policy", json=data)

    @classmethod
    @_format_api_output_to_stdout
    def remove_policy(cls, traffic_type: str) -> Response:
        data = {"traffic_type": traffic_type}
        return requests.delete(f"{cls._API_URL}/manager/manage_policy",
                               json=data)

    @staticmethod
    def show_manual() -> None:
        Manual.get()

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
            choices=["virtnet_create",
                     "virtnet_destroy",
                     "virtnet_status",
                     "create_policy",
                     "remove_policy",
                     "manual",
                     "test"],
            help="Escolha a ação a ser executada"
        )

        parser.add_argument("--traffic-type",
                            "-t",
                            type=str,
                            help="Tipo de tráfego alvo da política \
                                (ex: HTTP, FTP e VOiP)")

        parser.add_argument("--bandwidth",
                            "-b",
                            type=int,
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
            "virtnet_create": _Actions.virtnet_create,
            "virtnet_destroy": _Actions.virtnet_destroy,
            "virtnet_status": _Actions.virtnet_status,
            "create_policy": lambda: _Actions.create_policy(args.traffic_type,
                                                           args.bandwidth),
            "remove_policy": lambda: _Actions.remove_policy(args.traffic_type),
            "manual": _Actions.show_manual,
            "test": lambda: _Actions.run_tests(args.interactive,
                                                   args.file)
        }

        if args.action in action_map:
            action_map[args.action]()
        else:
            print("Ação desconhecida. Use --help para ver as opções.")


if __name__ == "__main__":
    Dispatcher.dispatch()

