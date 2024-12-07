from mininet.util import dumpNodeConnections
from mininet.net import Mininet

from src.virtnet import CustomTopo, VirtNetBuilder
from src.data import Error
from src.utils import Display, File


class VirtNetTests:
    def __init__(self):
        self._display = Display(prefix="tests")

    def builds_simple_topo_and_ping_all(self) -> None:
        self._display.title(f"Simulando uma rede padrão e pingando em " \
                            f"todos os hosts")

        simple_topo = {
            "hosts": ["h1", "h2"],
            "switches": [
                {
                    "id": "sw1",
                    "links": ["h1", "h2"]
                }
            ]
        }

        topo = CustomTopo(topo_schema=simple_topo)
        net = Mininet(topo=topo)

        dumpNodeConnections(net.hosts)

        net.start()
        net.pingAll()
        net.stop()

    def full_build_network_and_ping_all(self) -> None:
        self._display.title(f"Simulando uma rede com controlador faucet e " \
                            f"pingando todos os hosts")

        builder = VirtNetBuilder(
            topo_schema_path=File.get_config()["topo_schema_path"]
        )

        (build_result, net) = builder.build_network()
        
        if isinstance(build_result, Error):
            raise Exception(build_result.value)

        if net is not None:
            dumpNodeConnections(net.hosts)

            net.start()
            net.pingAll()
            net.stop()


if __name__ == "__main__":
    tests = VirtNetTests()

    tests.builds_simple_topo_and_ping_all()
    tests.full_build_network_and_ping_all()

