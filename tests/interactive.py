from mininet.cli import CLI

from src.management import Managers
from src.data import Error

class InteractiveTests:
    def __init__(self):
        self._managers = None
        self._net = None

    def _start_network_and_management(self) -> None:
        if self._managers is None:
            self._managers = Managers()

            build_result = self._managers.virtual_network.generate()

            if isinstance(build_result, Error):
                raise Exception(build_result.value)

        if self._net is None:
            self._net = self._managers.virtual_network.net

    def cli(self):
        print("[test] Instanciar topologia definida na configuração com \
                controlador faucet e invocar a CLI do Mininet")

        self._start_network_and_management()

        CLI(self._net)


if __name__ == "__main__":
    tests = InteractiveTests()
    tests.cli()

