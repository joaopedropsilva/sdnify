from mininet.cli import CLI

from src.management import VirtNetManagerFactory


if __name__ == "__main__":
    (err_manager, manager) = VirtNetManagerFactory.create()
    if manager is None:
        raise Exception(err_manager)

    (err_generation, is_network_up) = manager.virtnet.generate()
    if not is_network_up:
        raise Exception(err_generation)

    CLI(manager.virtnet.net)

