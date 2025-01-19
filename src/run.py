from src.parser import Parser
from src.config import NetConfig, FaucetConfig
from sys import argv


if __name__ == "__main__":
    FaucetConfig.clear()

    json_path = argv[-1]
    netconfig = NetConfig.load_json_from(path=json_path)
    NetConfig.validate(netconfig)

    parser = Parser(netconfig)
    translated_config = parser.build_config()

    FaucetConfig.update_with(translated_config)

