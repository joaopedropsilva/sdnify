from pathlib import Path
from enum import Enum
import json
import yaml



class _Messages(Enum):
    ErrorConfigNotFound = "Arquivo de configuração não encontrado."
    ErrorCouldNotReadConfig = "Não foi possível ler o arquivo de configuração."


class Config:
    _CFG_FILENAME = "config.json"
    _CFG_EXAMPLE_FILENAME = "config.example.json"

    @staticmethod
    def _get_project_path() -> Path:
        src_path = Path(__file__).parent.resolve()
        return Path(src_path).parent.resolve()

    @staticmethod
    def _read_from(path: Path) -> tuple[str, dict]:
        is_json = True if str(path).find("json") != -1 else False

        try:
            with open(path, "r") as file:
                if is_json:
                    return json.load(file)
                
                return yaml.safe_load(file)
        except FileNotFoundError:
            return _Messages.ErrorConfigNotFound.value, {}
        except (yaml.YAMLError, json.JSONDecodeError):
            return _Messages.ErrorCouldNotReadConfig.value, {}

    @classmethod
    def get(cls) -> tuple[str, dict]:
        config_path = Path(
            cls._get_project_path(),
            cls._CFG_FILENAME
        )
        config_example_path = Path(
            cls._get_project_path(),
            cls._CFG_EXAMPLE_FILENAME
        )


        (err, config) = cls._read_from(path=config_path)
        if err != "":
            return cls._read_from(path=config_example_path)

        return "", config


class FaucetConfig(Config):
    _FAUCET_PATH = "etc/faucet/faucet.yaml" 

    @classmethod
    def get(cls) -> tuple[str, dict]:
        faucet_path = Path(
            cls._get_project_path(),
            cls._FAUCET_PATH
        )

        return cls._read_from(path=faucet_path)

    @classmethod
    def update(cls, new_values: dict) -> None:
        pass

