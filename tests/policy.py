from src.management import VirtNetManagerFactory
from src.policy import Policy, PolicyTypes
from src.test_logger import TestLogger


class PolicyTests:
    def __init__(self):
        (err_manager, manager) = VirtNetManagerFactory.create(with_testing_features=True)
        if manager is None:
            raise Exception(err_manager)

        self._manager = manager

    def _iperf_between_hosts(self, host_options: dict) -> None:
        if self._manager.testing_features is None:
            return

        self._manager.testing_features.iperf_as_host(hostname="h1",
                                                     host_options=host_options,
                                                     logger=TestLogger.command)
        self._manager.testing_features.iperf_as_client(hostname="h2",
                                                       server_hostname="h1",
                                                       host_options=host_options,
                                                       logger=TestLogger.command)

        self._manager.testing_features.kill_iperf(hostname="h1",
                                                  logger=TestLogger.command)

    def pre_test_context(self) -> None:
        if not self._manager.network_exists:
            (err_creation, did_create) = self._manager.create_network()
            if not did_create:
                raise Exception(err_creation)

    def post_test_context(self) -> None:
        if self._manager.network_exists:
            (err_destruction, did_destroy) = self._manager.destroy_network()
            if not did_destroy:
                raise Exception(err_destruction)

    def create_test_policies(self) -> None:
        testlogger.message("criando políticas de classificação de pacote")

        types_and_bandwidths = [
            (PolicyTypes.HTTP, 30),
            (PolicyTypes.FTP, 10),
            (PolicyTypes.VOIP, 60)
         ]

        for t, b in types_and_bandwidths:
            policy = Policy(traffic_type=t, bandwidth=b)

            TestLogger.message(f"Criando política para " \
                               f"{policy.traffic_type.value} " \
                               f"({policy.bandwidth} Mbps)")

            (err_creation, did_create) = self._manager.create(policy=policy)
            if not did_create:
                raise Exception(err_creation)

    def simulate_http_traffic(self) -> None:
        TestLogger.message("Simulando tráfego http")

        self._iperf_between_hosts(host_options={
            "port": 80,
            "transport": "tcp",
            "bandwidth": "100m"
        })

    def simulate_ftp_traffic(self) -> None:
        TestLogger.message("Simulando tráfego ftp")

        self._iperf_between_hosts(host_options={
            "port": 21,
            "transport": "tcp",
            "bandwidth": "100m"
        })

    def simulate_voip_traffic(self) -> None:
        TestLogger.message("Simulando tráfego voip")

        self._iperf_between_hosts(host_options={
            "port": 5001,
            "transport": "udp",
            "bandwidth": "100m"
        })


if __name__ == "__main__":
    tests = PolicyTests()


    TestLogger.title("testes políticas de classificação de pacotes")
    tests.pre_test_context()

    tests.simulate_http_traffic()
    exit()
    tests.simulate_ftp_traffic()
    tests.simulate_voip_traffic()

    tests.post_test_context()
    tests.pre_test_context()

    tests.create_test_policies()
    tests.simulate_http_traffic()
    tests.simulate_ftp_traffic()
    tests.simulate_voip_traffic()

    tests.post_test_context()

