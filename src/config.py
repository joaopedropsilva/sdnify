from pathlib import Path
from src.context import Context
import json
import yaml


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
                    return ("", json.load(file))
                
                return ("", yaml.safe_load(file))
        except FileNotFoundError:
            return ("Arquivo de configuração não encontrado.", {})
        except (yaml.YAMLError, json.JSONDecodeError):
            return ("Não foi possível ler o arquivo de configuração.", {})

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

        return ("", config)


class FaucetConfig(Config):
    _FAUCET_PATH = "etc/faucet/faucet.yaml"

    @classmethod
    def get(cls) -> tuple[str, dict]:
        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        return cls._read_from(path=faucet_path)

    @classmethod
    def update_based_on(cls, context: Context) -> tuple[str, bool]:
        config = context.build_config()

        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        with open(faucet_path, "w") as file:
            file.write(yaml.dump(config, default_flow_style=False))

        return ("", True)

    @classmethod
    def clear(cls) -> tuple[str, bool]:
        faucet_path = Path(cls._get_project_path(), cls._FAUCET_PATH)
        with open(faucet_path, "w") as file:
            file.write(yaml.dump(None, default_flow_style=False))

        return ("", True)

