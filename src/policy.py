from enum import Enum


class PolicyTypes(Enum):
    VOIP = "voip"
    HTTP = "http"
    FTP = "ftp"


class Policy:
    def __init__(self, traffic_type: PolicyTypes, bandwidth: int):
        self.traffic_type = traffic_type
        self.bandwidth = bandwidth


class PolicyFactory:
    _MIN_BANDWIDTH = 1

    @classmethod
    def create_using(cls, policy_data: dict, max_bandwidth: int) \
            -> tuple[str, Policy | None]:
        bandwidth = int()
        try:
            bandwidth = policy_data["bandwidth"]
        except KeyError:
            return ("Largura de banda ausente.", None)

        traffic_type = str()
        try:
            tt = policy_data["traffic_type"]
            traffic_type = PolicyTypes[tt.upper()]
        except KeyError:
            return ("Tipo de tráfego inválido para política de classificação.",
                    None)

        if bandwidth < cls._MIN_BANDWIDTH or bandwidth > max_bandwidth:
            return ("Largura de banda inválida para política de classificação.",
                    None)

        policy = Policy(traffic_type=traffic_type, bandwidth=bandwidth)

        return ("", policy)

