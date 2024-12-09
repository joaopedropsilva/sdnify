from enum import Enum

from src.data import Success, Error


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

    def __init__(self, policy_data: dict, max_bandwidth: int):
        self._policy_data = policy_data
        self._max_bandwidth = max_bandwidth

    def create(self) -> tuple[Error | Success, Policy | None]:
        bandwidth = int()
        try:
            bandwidth = self._policy_data["bandwidth"]
        except KeyError:
            return Error.BandwidthNotFound, None

        traffic_type = str()
        try:
            tt = self._policy_data["traffic_type"]
            traffic_type = PolicyTypes[tt.upper()]
        except KeyError:
            return Error.InvalidPolicyTrafficType, None

        if bandwidth < self._MIN_BANDWIDTH \
            or bandwidth > self._max_bandwidth:
            return Error.InvalidPolicyBandwidth, None

        policy = Policy(traffic_type=traffic_type, bandwidth=bandwidth)

        return Success.OperationOk, policy

