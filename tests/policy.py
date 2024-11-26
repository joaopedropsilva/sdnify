from src.management import Managers
from src.data import Error, Policy, PolicyTypes

class PolicyTests:
    managers = Managers()

    @classmethod
    def _create_http_test_policy_with(cls, bandwidth: int) -> Policy:
        return Policy(name="id",
                      traffic_type=PolicyTypes.HTTP,
                      bandwidth=bandwidth)

    @classmethod
    def test_http_policy(cls):
        build_result = cls.managers.virtual_network.generate()

        print(build_result.value)

        if isinstance(build_result, Error):
            return

        policy = cls._create_http_test_policy_with(bandwidth=30)
        creation_result = cls.managers.flow.create(policy=policy)

        print(creation_result.value)
        if isinstance(creation_result, Error):
            return

        cls.managers.virtual_network.test()

if __name__ == "__main__":
    PolicyTests.test_http_policy()
