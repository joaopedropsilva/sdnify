from mininet.node import Host
from src.management import VirtNetManagerFactory
from src.policy import Policy, PolicyTypes
from src.utils import Display


class _IperfGenerator:
    def __init__(self,
                 port: int,
                 transport: str,
                 host_ip: str,
                 bandwidth: str):
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


class PolicyTests:
    def __init__(self):
        (err_manager, manager) = VirtNetManagerFactory.create()
        if manager is None:
            raise Exception(err_manager)

        self._manager = manager
        self._display = Display(prefix="tests")

    def pre_test_context(self) -> None:
        if not self._manager.network_already_up:
            (err_generation, is_network_up) = self._manager.virtnet.generate()
            if not is_network_up:
                raise Exception(err_generation)

    def post_test_context(self) -> None:
        if self._manager.network_already_up:
            (err_destruction, did_destroy) = self._manager.virtnet.destroy()
            if not did_destroy:
                raise Exception(err_destruction)

    def _issue_commands(self,
                        iperf_gen: _IperfGenerator,
                        hosts: tuple[Host, Host]) -> None:
        (h1, h2) = hosts

        host_cmd = iperf_gen.generate(command="iperf_as_host")
        self._display.command(host_cmd)
        h1.cmd(host_cmd)

        client_cmd = iperf_gen.generate(command="iperf_as_client")
        self._display.command(client_cmd)
        with h2.popen(client_cmd) as process:
            for line in process.stdout:
                print(line.strip())
        print("")

        kill_iperf = "kill %iperf"
        self._display.command(kill_iperf)
        h1.cmd(kill_iperf)

    def create_test_policies(self) -> None:
        self._display.title("Criando políticas de classificação de pacote")

        types_and_bandwidths = [
            (PolicyTypes.HTTP, 30),
            (PolicyTypes.FTP, 10),
            (PolicyTypes.VOIP, 60)
         ]

        for t, b in types_and_bandwidths:
            policy = Policy(traffic_type=t, bandwidth=b)

            self._display.message(f"Criando política para " \
                                  f"{policy.traffic_type.value} " \
                                  f"({policy.bandwidth} Mbps)")

            (err_creation, did_create) = self._manager.create(policy=policy)
            if not did_create:
                raise Exception(err_creation)

        self._display.message(f"Políticas criadas com sucesso!")

    def simulate_http_traffic(self) -> None:
        self._display.title("Simulando tráfego http")

        assert self._manager.virtnet.net is not None, \
        self._display.message("rede virtual não instanciada!")

        h1, h2 = self._manager.virtnet.net.get("h1", "h2")

        iperf_generator = _IperfGenerator(port=80,
                                          transport="tcp",
                                          host_ip=h1.IP(),
                                          bandwidth="100m")

        self._issue_commands(iperf_gen=iperf_generator,
                             hosts=(h1, h2))

    def simulate_ftp_traffic(self) -> None:
        self._display.title("Simulando tráfego ftp")

        assert self._manager.virtnet.net is not None, \
        self._display.message("rede virtual não instanciada!")

        h1, h2 = self._manager.virtnet.net.get("h1", "h2")

        iperf_generator = _IperfGenerator(port=21,
                                          transport="tcp",
                                          host_ip=h1.IP(),
                                          bandwidth="100m")

        self._issue_commands(iperf_gen=iperf_generator,
                             hosts=(h1, h2))

    def simulate_voip_traffic(self) -> None:
        self._display.title("Simulando tráfego voip")

        assert self._manager.virtnet.net is not None, \
        self._display.message("rede virtual não instanciada!")


        h1, h2 = self._manager.virtnet.net.get("h1", "h2")

        iperf_generator = _IperfGenerator(port=5001,
                                          transport="udp",
                                          host_ip=h1.IP(),
                                          bandwidth="100m")

        self._issue_commands(iperf_gen=iperf_generator,
                             hosts=(h1, h2))


if __name__ == "__main__":
    tests = PolicyTests()

    tests.pre_test_context()

    tests.simulate_http_traffic()
    tests.simulate_ftp_traffic()
    tests.simulate_voip_traffic()

    tests.post_test_context()
    tests.pre_test_context()

    tests.create_test_policies()
    exit()
    tests.simulate_http_traffic()
    tests.simulate_ftp_traffic()
    tests.simulate_voip_traffic()

    tests.post_test_context()

