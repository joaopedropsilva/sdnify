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


class File:
    @staticmethod
    def get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @staticmethod
    def read_json_from(filepath: str) -> dict:
        try:
            path = Path(filepath)
        
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
            with open(path, "r", encoding="utf-8") as file:
                data = load(file)
                
            return data
        
        except FileNotFoundError:
            return {}

    @classmethod
    def get_config(cls) -> dict:
        config_path = Path(
            cls.get_project_path(),
            "config.json"
        )
        config_example_path = Path(
            cls.get_project_path(),
            "config.example.json"
        )

        config = cls.read_json_from(str(config_path.resolve()))
        config_example = cls.read_json_from(str(config_example_path.resolve()))

        return config \
                if config_path.exists() \
                else config_example

    @classmethod
    def update_config(cls, new_values: dict) -> None:
        config = cls.get_config()
        config.update(new_values)

        config_path = Path(
            cls.get_project_path(),
            "config.json"
        )

        config_example_path = Path(
            cls.get_project_path(),
            "config.example.json"
        )

        path = config_path if config_path.exists() else config_example_path

        with open(path, "w") as file:
            dump(config, file, indent=4)


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

