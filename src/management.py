from src.config import FaucetConfig
from src.policy import Policy, PolicyTypes
from src.virtnet import VirtNet, TestingFeatures
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

    def create_network(self) -> tuple[str, bool]:
        return ("Não implementado.", False)

    def destroy_network(self) -> tuple[str, bool]:
        return ("Não implementado.", False)

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
    def __init__(self,
                 topology: Topology,
                 context: Context,
                 with_testing_features: bool = False):
        super().__init__(topology=topology, context=context)
        self._virtnet = VirtNet(topo_schema=self._topology.schema,
                                enable_testing_features=with_testing_features)

    @property
    def network_exists(self) -> bool:
        return self._virtnet.network_exists

    @property
    def testing_features(self) -> TestingFeatures | None:
        return self._virtnet.testing_features

    def create_network(self) -> tuple[str, bool]:
        (err_generation, did_generate) = self._virtnet.generate()
        if not did_generate:
            return (err_generation, False)

        (err_config, did_update) = \
                FaucetConfig.update_based_on(context=self._context)
        if not did_update:
            return (err_config, False)

        (err_start, did_start) = self._virtnet.start()
        if not did_start:
            return (err_start, False)

        return ("", True)

    def destroy_network(self) -> tuple[str, bool]:
        (err_stop, did_stop) = self._virtnet.stop()
        if not did_stop:
            return (err_stop, False)

        (err_destruction, did_destroy) = self._virtnet.destroy()
        if not did_destroy:
            return (err_destruction, False)

        return ("", True)


class VirtNetManagerFactory:
    @staticmethod
    def create(with_testing_features: bool = False) -> tuple[str, VirtNetManager | None]:
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

        return ("", VirtNetManager(topology=topology,
                                   context=context,
                                   with_testing_features=with_testing_features))

