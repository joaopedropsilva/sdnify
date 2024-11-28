from src.management import Managers
from src.data import Error, Policy, PolicyTypes

class PolicyTests:
    managers = Managers()

    @classmethod
    def test_http_policy(cls):
        build_result = cls.managers.virtual_network.generate()

        print(build_result.value)

        if isinstance(build_result, Error):
            return

        policy = Policy(traffic_type=PolicyTypes.HTTP,
                        bandwidth=30)
        creation_result = cls.managers.flow.create(policy=policy)

        print(creation_result.value)
        if isinstance(creation_result, Error):
            return

        #cls.managers.virtual_network.invoke_cli()

if __name__ == "__main__":
    PolicyTests.test_http_policy()
