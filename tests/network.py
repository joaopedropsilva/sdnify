from mininet.util import dumpNodeConnections
from mininet.net import Mininet

from src.data import CustomTopo, NetworkBuilder, Error
from src.utils import File

class Network:
    _simple_topo = {
        "hosts": ["h1", "h2"],
        "switches": [
            {
                "id": "sw1",
                "links": ["h1", "h2"]
            }
        ]
    }

    @staticmethod
    def _ping_all(net: Mininet) -> None:
        net.start()

        dumpNodeConnections(net.hosts)
        net.pingAll()

        net.stop()

    @classmethod
    def builds_custom_topo_and_ping_all(cls) -> None:
        topo = CustomTopo(topo_schema=cls._simple_topo)
        net = Mininet(topo=topo)

        cls._ping_all(net)

    @classmethod
    def full_build_network_and_ping_all(cls) -> None:
        builder = NetworkBuilder(
            topo_schema_path=File.get_config()["topo_schema_path"]
        )

        (build_result, net) = builder.build_network()
        
        if isinstance(build_result, Error):
            raise Exception(build_result.value)

        cls._ping_all(net)

if __name__ == "__main__":
    Network.full_build_network_and_ping_all()
