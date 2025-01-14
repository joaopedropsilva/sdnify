from argparse import ArgumentParser
from pathlib import Path
from subprocess import run


class _Manual:
    _DOC_FILE = "README.md"

    @staticmethod
    def _get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @classmethod
    def get(cls) -> None:
        with open(Path(cls._get_project_path(), cls._DOC_FILE), "r") as file:
            print(file.read())


class _Actions:
    @staticmethod
    def show_manual() -> None:
        _Manual.get()

    @staticmethod
    def run_tests(interactive: bool, test_file: str) -> None:
        script = []

        if interactive:
            script = ["python", "-m", "tests.interactive"]

        if test_file is not None:
            script = ["python", "-m", f"tests.{test_file}"]

        try:
            run(script)
        except KeyboardInterrupt:
            print("kbd")


class Dispatcher:
    @staticmethod
    def _create_arg_parser() -> ArgumentParser:
        parser = ArgumentParser(description="SDNify: Gerenciador de Redes SDN")

        parser.add_argument(
            "action",
            type=str,
            choices=["manual",
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

