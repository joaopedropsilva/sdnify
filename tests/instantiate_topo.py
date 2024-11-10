from src.network import Topology
from mininet.util import dumpNodeConnections

def ping_all(net: Mininet) -> None:
    net.start()

    dumpNodeConnections(net.hosts)
    net.pingAll()

    net.stop()

def test_with_default_controller(topology: dict, test_name: str) -> None:
    topo = Topo(topology)
    net = Mininet(topo=topo)

    if test_name == "ping_all":
        ping_all(net)

if __name__ == "__main__":
    topology = {
        "hosts": ["h1", "h2"],
        "switches": [
            {
                "id": "sw1",
                "links": ["h1", "h2"]
            }
        ]
    }

    test_with_default_controller(topology=topology, test_name="ping_all")

