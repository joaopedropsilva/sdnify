from src.parser import Parser
from src.config import NetConfig, FaucetConfig


if __name__ == "__main__":

    netconfig = NetConfig.load_json_from(path="examples/simple_network")
    NetConfig.validate(netconfig)

    parser = Parser(netconfig)
    translated_config = parser.build_config()

    FaucetConfig.update_with(translated_config)

