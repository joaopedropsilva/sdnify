from src.management import VirtNetManagerFactory


if __name__ == "__main__":
    (err_manager, manager) = VirtNetManagerFactory.create(with_testing_features=True)
    if manager is None:
        raise Exception(err_manager)

    (err_creation, did_create) = manager.create_network()
    if not did_create:
        raise Exception(err_creation)

    if manager.testing_features is None:
        exit(1)

    manager.testing_features.invoke_cli()

