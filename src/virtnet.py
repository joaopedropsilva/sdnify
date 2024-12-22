from mininet.node import RemoteController
from mininet.clean import Cleanup
from mininet.net import Mininet
from mininet.topo import Topo
from mininet.net import Mininet


class _MininetTopoBuilder(Topo):
    def build(self, schema: dict) -> None:
        for dp in schema["dps"]:
            dp_name = dp["name"]

            self.addSwitch(dp_name)

            for host in dp["hosts"]:
                self.addHost(host)
                self.addLink(host, dp_name)


class _VirtNetFactory():
    _OPF_PORT = 6653

    @classmethod
    def create_using(cls, topo_schema: dict) -> tuple[str, Mininet | None]:
        net = None
        try:
            net = Mininet(topo=_MininetTopoBuilder(topo_schema=topo_schema))

            net.addController(name="c1",
                              controller=RemoteController,
                              ip="faucet",
                              port=cls._OPF_PORT)

            net.addController(name="c2",
                              controller=RemoteController,
                              ip="gauge",
                              port=cls._OPF_PORT)

            return ("", net)
        except Exception:
            return ("Falha ao instanciar a rede virtual.", None)


class VirtNet:
    def __init__(self, topo_schema: dict):
        self._net = None
        self._topo_schema = topo_schema

    @property
    def net(self) -> Mininet | None:
        return self._net

    def generate(self) -> tuple[str, bool]:
        (err, net) = _VirtNetFactory.create_using(topo_schema=self._topo_schema)
        if err != "":
            return (err, False)

        if net is not None:
            self._net = net
            self._net.start()

        return ("", True)

    def destroy(self) -> tuple[str, bool]:
        if self._net is not None:
            try:
                self._net.stop()
                self._net = None
            except Exception:
                return ("Falha ao destruir a rede virtual.", False)

        Cleanup()

        return ("", True)

