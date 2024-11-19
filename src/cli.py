from argparse import ArgumentParser
import requests


# Padronizar output em STDOUT
class Actions:
    __API_URL = "http://127.0.0.1:5000"

    @classmethod
    def create_network(cls) -> None:
        response = requests.post(f"{cls.__API_URL}/start")

        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def destroy_network(cls) -> None:
        response = requests.get(f"{cls.__API_URL}/destroy")

        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def create_policy(cls, name: str, protocol: str, bandwidth: float) -> None:
        # Remove name
        policy = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.post(f"{cls.__API_URL}/manage_policy", json=policy)

        print(f"STATUS: {response.status_code} - {response.text}")


    @classmethod
    def update_policy(cls, name: str, protocol: str, bandwidth: float) -> None:
        policy = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.put(f"{cls.__API_URL}/manage_policy", json=policy)

        print(f"STATUS: {response.status_code} - {response.text}")


    @classmethod
    def remove_policy(cls, protocol: str) -> None:
        policy = {"protocol": protocol}
        response = requests.delete(f"{cls.__API_URL}/manage_policy", json=policy)
        
        print(f"STATUS: {response.status_code} - {response.text}")

    @classmethod
    def show_network_state(cls) -> None:
        response = requests.get(f"{cls.__API_URL}/get_statistics")

        print(f"STATUS: {response.status_code} - {response.text}")

    @staticmethod
    def show_manual() -> None:
        pass

class Dispatcher:
    @staticmethod
    def __create_arg_parser() -> ArgumentParser:
        parser = ArgumentParser(description="Gerenciador de Redes SDN")
        parser.add_argument(
            "action",
            type=str,
            choices=["create_network",
                     "destroy_network",
                     "create_policy",
                     "update_policy",
                     "remove_policy",
                     "show_network_state",
                     "show_manual"],
            help="Escolha a ação a ser executada"
        )

        parser.add_argument("--file",
                            type=str,
                            help="Caminho de um arquivo JSON para criar a rede")
        parser.add_argument("--name",
                            type=str,
                            help="Nome da política para criar ou atualizar")
        parser.add_argument("--protocol",
                            type=str,
                            help="Protocolo da política (ex: HTTP, FTP e RTP)")
        parser.add_argument("--bandwidth",
                            type=float,
                            help="Largura de banda para a política")
        return parser
    
    @classmethod
    def dispatch(cls):
        parser = cls.__create_arg_parser()

        args = parser.parse_args()
        action_map = {
            "create_network": Actions.create_network,
            "destroy_network": Actions.destroy_network,
            "create_policy": lambda: Actions.create_policy(args.name,
                                                           args.protocol,
                                                           args.bandwidth),
            "update_policy": lambda: Actions.update_policy(args.name,
                                                           args.protocol,
                                                           args.bandwidth),
            "remove_policy": lambda: Actions.remove_policy(args.protocol),
            "show_network_state": Actions.show_network_state,
            "show_manual": Actions.show_manual
        }

        if args.action in action_map:
            action_map[args.action]()
        else:
            print("Ação desconhecida. Use --help para ver as opções.")

if __name__ == "__main__":
    Dispatcher.dispatch()

