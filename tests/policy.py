from src.management import Managers
from src.data import Error, Policy, PolicyTypes
from src.utils import Display


class CommandGenerator:
    def __init__(self,
                 port: int,
                 transport: str,
                 host_ip: str,
                 bandwidth: str):
        self._port = port
        self._transport = "" if transport == "tcp" else "-u"
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
        self._managers = None
        self._net = None
        self._display = Display(prefix="tests")

    def start_network_and_management(self) -> None:
        if self._managers is None:
            self._managers = Managers()

            build_result = self._managers.virtual_network.generate()

            if isinstance(build_result, Error):
                raise Exception(build_result.value)

        if self._net is None:
            self._net = self._managers.virtual_network.net

    def create_test_policies(self) -> None:
        pass

    def simulate_http_traffic(self) -> None:
        self._display.title("Simulando tráfego http")
        pass

    def simulate_ftp_traffic(self) -> None:
        self._display.title("Simulando tráfego ftp")

        if self._net is None:
            return

        h1, h2 = self._net.get("h1", "h2")

        command_gen = CommandGenerator(port=21,
                                       transport="tcp",
                                       host_ip=h1.IP(),
                                       bandwidth="100m")
        
        host_cmd = command_gen.generate(command="iperf_as_host")
        self._display.command(host_cmd)
        h1.cmd(host_cmd)

        client_cmd = command_gen.generate(command="iperf_as_client")
        self._display.command(client_cmd)
        with h2.popen(client_cmd) as process:
            for line in process.stdout:
                print(line.strip())

        kill_iperf = "kill %iperf"
        self._display.command(kill_iperf)
        h1.cmd(kill_iperf)

    def simulate_voip_traffic(self) -> None:
        self._display.title("Simulando tráfego voip")

    def stop_network(self) -> None:
        if self._net is None:
            return

        self._net.stop()


if __name__ == "__main__":
    tests = PolicyTests()

    tests.start_network_and_management()
    tests.create_test_policies()

    tests.simulate_http_traffic()
    tests.simulate_ftp_traffic()
    tests.simulate_voip_traffic()

    tests.stop_network()

