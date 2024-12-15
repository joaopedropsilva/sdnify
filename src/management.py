from typing import List

from src.config import FaucetConfig
from src.utils import File
from src.data import Success, Error
from src.policy import Policy, PolicyTypes
from src.virtnet import VirtNet


class FlowManager:
    _MIN_BANDWIDTH = 1
    
    def __init__(self):
        self._project_config = File.get_config()
        self._policies: List[Policy] = []

    def process_alerts(self, alerts: dict) -> Success | Error:
        return Success.OperationOk

    def redirect_traffic(self) -> Success | Error:
        return Success.OperationOk

    def create(self, policy: Policy) -> Success | Error:
        policy_exist = len([p for p in self._policies \
                            if p.traffic_type == policy.traffic_type]) != 0

        if not policy_exist:
            self._policies.append(policy)

        (_, did_config_update) = \
                FaucetConfig.update_based_on(
                        context_data={"policies": self._policies})

        if not did_config_update:
            return Error.ConfigWriteFailure

        return Success.ConfigWriteOk

    def remove_policy_by(self, traffic_type: PolicyTypes) -> Success | Error:
        if not any(p.traffic_type == traffic_type \
                   for p in self._policies):
            return Error.PolicyNotFound  

        policy = [p for p in self._policies
                  if p.traffic_type == traffic_type][0]

        self._policies.remove(policy)

        (_, did_config_update) = \
                FaucetConfig.update_based_on(
                        context_data={"policies": self._policies})

        if not did_config_update:
            return Error.ConfigWriteFailure

        return Success.OperationOk


class NetworkManager:
    def __init__(self):
        self._flow = FlowManager()

    @property
    def flow(self) -> FlowManager:
        return self._flow


class VirtNetManager(NetworkManager):
    def __init__(self):
        super().__init__()
        self._virtnet = VirtNet()

    @property
    def virtnet(self) -> VirtNet:
        return self._virtnet

    @property
    def network_already_up(self) -> bool:
        return True if self._virtnet.net is not None else False

