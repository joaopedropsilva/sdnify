from pathlib import Path
from json import load, dump


class Display:
    def __init__(self, prefix: str):
        self._prefix = prefix

    def _get_decorator(self) -> str:
        return "\n" + f"{120 * '='}" + "\n"

    def title(self, content: str) -> None:
        print(f"{self._get_decorator()}" \
              f"\t{content.upper()}" \
              f"{self._get_decorator()}")

    def command(self, content: str) -> None:
        print(f"[{self._prefix}:command] {content}\n")

    def message(self, content: str) -> None:
        print(f"[{self._prefix}:message] {content}\n")


class Manual:
    _DOC_FILE = "README.md"

    @staticmethod
    def _get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @classmethod
    def get(cls) -> None:
        with open(Path(cls._get_project_path(), cls._DOC_FILE), "r") as file:
            print(file.read())

