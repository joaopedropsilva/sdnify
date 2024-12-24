from src.utils import Display
from src.management import VirtNetManagerFactory


class VirtNetTests:
    def __init__(self):
        (err_manager, manager) = VirtNetManagerFactory.create(with_testing_features=True)
        if manager is None:
            raise Exception(err_manager)

        (err_creation, did_create) = manager.create_network()
        if not did_create:
            raise Exception(err_creation)

        self._manager = manager
        self._display = Display(prefix="tests")

    def post_test(self) -> None:
        (err_destruction, did_destroy) = self._manager.destroy_network()
        if not did_destroy:
            raise Exception(err_destruction)

    def ping_all(self) -> None:
        self._display.title("Pingando todos os hosts criados na rede virtual")
        if self._manager.testing_features is None:
            return

        self._manager.testing_features.ping_all()


if __name__ == "__main__":
    tests = VirtNetTests()

    tests.ping_all()
    tests.post_test()

