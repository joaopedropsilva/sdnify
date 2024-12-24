from pathlib import Path


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

