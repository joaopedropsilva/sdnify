from mininet.node import Host

from src.management import VirtNetManager
from src.data import Error, Policy, PolicyTypes
from src.utils import Display, File


class CommandGenerator:
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
        self._manager = None
        self._net = None
        self._display = Display(prefix="tests")

    def _issue_commands(self,
                        command_gen: CommandGenerator,
                        hosts: tuple[Host, Host]) -> None:
        (h1, h2) = hosts

        host_cmd = command_gen.generate(command="iperf_as_host")
        self._display.command(host_cmd)
        h1.cmd(host_cmd)

        client_cmd = command_gen.generate(command="iperf_as_client")
        self._display.command(client_cmd)
        with h2.popen(client_cmd) as process:
            for line in process.stdout:
                print(line.strip())
        print("")

        kill_iperf = "kill %iperf"
        self._display.command(kill_iperf)
        h1.cmd(kill_iperf)

    def start_network_and_management(self) -> None:
        if self._manager is None:
            self._manager = VirtNetManager()

        if not self._manager.network_already_up:
            build_result = self._manager.virtnet.generate()

            if isinstance(build_result, Error):
                raise Exception(build_result.value)

        if self._net is None:
            self._net = self._manager.virtnet.net

    def stop_network(self) -> None:
        if self._manager is None:
            return

        destruction_result = self._manager.virtnet.destroy()

        if isinstance(destruction_result, Error):
            raise Exception(destruction_result.value)

    def create_test_policies(self) -> None:
        self._display.title("Criando políticas de classificação de pacote")

        self._manager = VirtNetManager()

        bandwidths = File.get_config()["bandwidths"]

        types_and_bandwidths = [
            (PolicyTypes.HTTP, bandwidths["http"]),
            (PolicyTypes.FTP, bandwidths["ftp"]),
            (PolicyTypes.VOIP, bandwidths["voip"])
         ]

        for t, b in types_and_bandwidths:
            policy = Policy(traffic_type=t, bandwidth=b)

            self._display.message(f"Criando política para " \
                                  f"{policy.traffic_type.value} " \
                                  f"({policy.bandwidth} Mbps)")

            creation_result = self._manager.flow.create(policy=policy)

            if isinstance(creation_result, Error):
                raise Exception(creation_result.value)

        File.update_config({"limit_bandwidth": True})

        self._display.message(f"Políticas criadas com sucesso, execute o " \
                              f"script novamente para executar os testes")

    def simulate_http_traffic(self, qos: bool = False) -> None:
        title = f"Simulando tráfego http " \
                f"{'(sem políticas de classificação)' if not qos else ''}"
        self._display.title(title)

        if self._net is None:
            return

        h1, h2 = self._net.get("h1", "h2")

        command_gen = CommandGenerator(port=80,
                                       transport="tcp",
                                       host_ip=h1.IP(),
                                       bandwidth="100m")

        self._issue_commands(command_gen=command_gen,
                             hosts=(h1, h2))

    def simulate_ftp_traffic(self, qos: bool = False) -> None:
        title = f"Simulando tráfego ftp " \
                f"{'(sem políticas de classificação)' if not qos else ''}"
        self._display.title(title)

        if self._net is None:
            return

        h1, h2 = self._net.get("h1", "h2")

        command_gen = CommandGenerator(port=21,
                                       transport="tcp",
                                       host_ip=h1.IP(),
                                       bandwidth="100m")

        self._issue_commands(command_gen=command_gen,
                             hosts=(h1, h2))

    def simulate_voip_traffic(self, qos: bool = False) -> None:
        title = f"Simulando tráfego voip " \
                f"{'(sem políticas de classificação)' if not qos else ''}"
        self._display.title(title)

        if self._net is None:
            return

        h1, h2 = self._net.get("h1", "h2")

        command_gen = CommandGenerator(port=5001,
                                       transport="udp",
                                       host_ip=h1.IP(),
                                       bandwidth="100m")

        self._issue_commands(command_gen=command_gen,
                             hosts=(h1, h2))


if __name__ == "__main__":
    tests = PolicyTests()

    bandwidth_limit_exist = File.get_config()["limit_bandwidth"]

    tests.start_network_and_management()

    tests.simulate_http_traffic(qos=bandwidth_limit_exist)
    tests.simulate_ftp_traffic(qos=bandwidth_limit_exist)
    tests.simulate_voip_traffic(qos=bandwidth_limit_exist)

    tests.stop_network()

    if not bandwidth_limit_exist:
        tests.create_test_policies()

