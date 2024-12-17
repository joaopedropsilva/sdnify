from mininet.cli import CLI

from src.management import VirtNetManager


if __name__ == "__main__":
    manager = VirtNetManager()

    (err, is_network_up) = manager.virtnet.generate()
    if err != "":
        raise Exception(err)

    CLI(manager.virtnet.net)

