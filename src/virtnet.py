from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.clean import Cleanup
from mininet.topo import Topo
from mininet.net import Mininet
from typing import Callable


class _MininetTopoBuilder(Topo):
    def build(self, schema: dict) -> None:
        for dp in schema["dps"]:
            dp_name = dp["name"]

            self.addSwitch(dp_name)

            for host in dp["hosts"]:
                self.addHost(host["name"])
                self.addLink(host["name"], dp_name)


class _MininetFactory():
    _OPF_PORT = 6653

    @classmethod
    def create_using(cls, topo_schema: dict) -> tuple[str, Mininet | None]:
        net = None
        try:
            net = Mininet(topo=_MininetTopoBuilder(topo_schema))

            net.addController(name="c1",
                              controller=RemoteController,
                              ip="faucet",
                              port=cls._OPF_PORT)

            net.addController(name="c2",
                              controller=RemoteController,
                              ip="gauge",
                              port=cls._OPF_PORT)

            return ("", net)
        except Exception as err:
            return (f"Falha ao instanciar a rede virtual: {repr(err)}", None)


class _IperfGenerator:
    def __init__(self,
                 port: int,
                 transport: str,
                 host_ip: str = "",
                 bandwidth: str = ""):
        self._port = port
        self._transport = "" if transport == "tcp" else " -u"
        self._host_ip = host_ip
        self._bandwidth = bandwidth

    def _iperf_as_host(self) -> str:
        return f"iperf -s -p {self._port}{self._transport} &"

    def _iperf_as_client(self) -> str:
        return f"iperf -c {self._host_ip} -p {self._port}" \
               f"{self._transport} " \
               f"-i 1 -t 10 -b {self._bandwidth}"

    def generate(self, command: str) -> str:
        if command == "iperf_as_host":
            return self._iperf_as_host()
        elif command == "iperf_as_client":
            return self._iperf_as_client()

        return ""


class TestingFeatures:
    def __init__(self, net: Mininet):
        self._net = net

    def ping_all(self) -> None:
        self._net.pingAll()

    def invoke_cli(self) -> None:
        CLI(self._net)

    def iperf_as_host(self, hostname: str, host_options: dict, logger: Callable) -> None:
        host = self._net.get(hostname)

        gen = _IperfGenerator(port=host_options["port"],
                              transport=host_options["transport"])
        command = gen.generate(command="iperf_as_host")

        logger(command)
        host.cmd(command)

    def iperf_as_client(self, hostname: str, host_options: dict, logger: Callable) -> None:
        host = self._net.get(hostname)

        gen = _IperfGenerator(port=host_options["port"],
                              transport=host_options["transport"],
                              host_ip=host.IP(),
                              bandwidth=host_options["bandwidth"])
        command = gen.generate(command="iperf_as_client")

        logger(command)
        with host.popen(command) as process:
            for line in process.stdout:
                print(line.strip())

    def kill_iperf(self, hostname: str, logger: Callable) -> None:
        host = self._net.get(hostname)

        command = "kill %iperf"

        logger(command)
        host.cmd(command)


class VirtNet:
    def __init__(self, topo_schema: dict, enable_testing_features: bool = False):
        self._net = None
        self._topo_schema = topo_schema
        self._is_testing_enabled = enable_testing_features
        self._testing_features = None

    @property
    def network_exists(self) -> bool:
        return False if self._net is None else True

    @property
    def testing_features(self) -> TestingFeatures | None:
        return self._testing_features

    def generate(self) -> tuple[str, bool]:
        if self._net is not None:
            return ("", True)

        (err_mininet, net) = \
                _MininetFactory.create_using(topo_schema=self._topo_schema)
        if net is None:
            return (err_mininet, False)

        if self._is_testing_enabled:
            self._testing_features = TestingFeatures(net=net)

        self._net = net

        return ("", True)

    def start(self) -> tuple[str, bool]:
        if self._net is None:
            return ("Falha ao iniciar a rede virtual: rede virtual não instanciada",
                    False)
        try:
            self._net.start()
        except Exception as err:
            return (f"Falha ao iniciar a rede virtual: {repr(err)}",
                    False)
        
        return ("", True)

    def stop(self) -> tuple[str, bool]:
        if self._net is None:
            return ("Falha ao interromper a rede virtual: rede virtual não instanciada",
                    False)
        try:
            self._net.stop()
        except Exception as err:
            return (f"Falha ao interromper a rede virtual: {repr(err)}",
                    False)

        return ("", True)

    def destroy(self) -> tuple[str, bool]:
        if self._net is None:
            return ("Falha ao destruir a rede virtual: rede virtual não instanciada",
                    False)

        try:
            self._net = None
            Cleanup()
        except Exception as err:
            return (f"Falha ao destruir a rede virtual: {repr(err)}", False)

        return ("", True)

