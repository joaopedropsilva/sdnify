from mininet.cli import CLI

from src.management import VirtNetManager
from src.utils import Display


class RedirectTests:
    def __init__(self):
        self.manager = VirtNetManager()
        self.net = self.manager.virtnet.net
        self._display = Display(prefix="tests")

    def create_redirection(self) -> None:
        self._display.title("Criando regras de redirecionamento")

        (err, was_redirection_created) = manager.redirect_traffic()
        if not was_redirection_created:
            raise Exception(err)

        self._display.message(f"Redirecionamento criado com sucesso!")

    def test(self) -> None:
        pass


if __name__ == "__main__":
    tests = RedirectTests()

    tests.create_redirection()

    tests.manager.virtnet.generate()
    tests.net = tests.manager.virtnet.net

    CLI(tests.net)

