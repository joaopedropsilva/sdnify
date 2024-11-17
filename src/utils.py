from pathlib import Path
from json import load


class File:
    @staticmethod
    def get_project_path():
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

class Manual:
    @staticmethod
    def get_manual() -> None:
        """
            Retorna o manual do controlador completo
        """
        pass

    @staticmethod
    def get_rules() -> None:
        """
            Retorna as regras definidas no manual do controlador 
        """
        pass

    @staticmethod
    def get_commands() -> None:
        """
            Retorna os comandos definidos no manual do controlador
        """
        pass

