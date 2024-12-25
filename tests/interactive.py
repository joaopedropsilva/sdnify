from src.management import VirtNetManagerFactory
from src.config import FaucetConfig


if __name__ == "__main__":
    (err_manager, manager) = VirtNetManagerFactory.create(with_testing_features=True)
    if manager is None:
        raise Exception(err_manager)

    (err_creation, did_create) = manager.create_network()
    if not did_create:
        raise Exception(err_creation)

    if manager.testing_features is None:
        exit(1)

    try:
        manager.testing_features.invoke_cli()
    except KeyboardInterrupt:
        pass
    finally:
        (err_clear, was_cleared) = FaucetConfig.clear()
        if not was_cleared:
            raise Exception(err_clear)

