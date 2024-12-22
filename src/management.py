from src.config import FaucetConfig
from src.policy import Policy, PolicyTypes
from src.virtnet import VirtNet
from src.config import Config
from src.topology import Topology, TopologyFactory
from src.context import Context, ContextFactory


class NetworkManager:
    def __init__(self, topology: Topology, context: Context):
        self._topology = topology
        self._context = context

    @property
    def topology(self) -> Topology:
        return self._topology

    @property
    def context(self) -> Context:
        return self._context

    def process_alerts(self, alerts: dict) -> tuple[str, bool]:
        return ("", True)

    def redirect_traffic(self) -> tuple[str, bool]:
        # Remover dependência do config
        (err, config) = Config.get()
        if err != "":
            return err, False
        self._context.redirect = config["redirect"]

        return FaucetConfig.update_based_on(context=self._context)

    def create(self, policy: Policy) -> tuple[str, bool]:
        policy_exist = len([p for p in self._context.policies \
                            if p.traffic_type == policy.traffic_type]) != 0

        if not policy_exist:
            self._context.policies.append(policy)

        return FaucetConfig.update_based_on(context=self._context)

    def remove_policy_by(self, traffic_type: PolicyTypes) -> tuple[str, bool]:
        if not any(p.traffic_type == traffic_type \
                   for p in self._context.policies):
            return ("Política de tráfego não encontrada.", False)

        policy = [p for p in self._context.policies
                  if p.traffic_type == traffic_type][0]

        self._context.policies.remove(policy)

        return FaucetConfig.update_based_on(context=self._context)


class VirtNetManager(NetworkManager):
    def __init__(self, topology: Topology, context: Context):
        super().__init__(topology=topology, context=context)
        self._virtnet = VirtNet(topo_schema=self._topology.schema)

    @property
    def virtnet(self) -> VirtNet:
        return self._virtnet

    @property
    def network_already_up(self) -> bool:
        return True if self._virtnet.net is not None else False


class VirtNetManagerFactory:
    @staticmethod
    def create() -> tuple[str, VirtNetManager | None]:
        (err_config, project_config) = Config.get()
        if err_config != "":
            return (err_config, None)

        (err_topology, topology) = TopologyFactory \
                .create_from(config=project_config)
        if topology is None:
            return (err_topology, None)

        (err_validation, is_topo_valid) = topology.validate()
        if not is_topo_valid:
            return (err_validation, None)

        (err_context, context) = ContextFactory \
                .create_from(context_data={"topology": topology})
        if context is None:
            return (err_context, None)

        return ("", VirtNetManager(topology=topology, context=context))

