from mininet.util import dumpNodeConnections
from src.utils import Display
from src.management import VirtNetManagerFactory


class VirtNetTests:
    def __init__(self):
        (err_manager, manager) = VirtNetManagerFactory.create()
        if manager is None:
            raise Exception(err_manager)

        (err_generation, is_network_up) = manager.virtnet.generate()
        if not is_network_up:
            raise Exception(err_generation)

        self._manager = manager
        self._display = Display(prefix="tests")

    def ping_all(self) -> None:
        self._display.title("Pingando todos os hosts criados na rede virtual")

        if self._manager.virtnet.net is not None:
            dumpNodeConnections(self._manager.virtnet.net.hosts)

            self._manager.virtnet.net.start()
            self._manager.virtnet.net.pingAll()
            self._manager.virtnet.net.stop()


if __name__ == "__main__":
    tests = VirtNetTests()

    tests.ping_all()

