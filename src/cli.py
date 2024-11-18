import argparse
import requests


class Actions:
    BASE_URL = "http://127.0.0.1:5000"  # URL do Flask Server onde a API está rodando

    @classmethod
    def create_network(cls, file: str) -> None:
        with open(file, 'r') as json_file:
            config_data = json_file.read()

        response = requests.post(f"{cls.BASE_URL}/start", data=config_data)

        if response.status_code == 200:
            print("Rede criada com sucesso e serviço de monitoramento inicializado.")
        else:
            print(f"Erro na criação da rede: Código HTTP {response.status_code} - {response.text}")

    @classmethod
    def destroy_network(cls) -> None:
        response = requests.get(f"{cls.BASE_URL}/destroy")

        if response.status_code == 200:
            print("Rede destruída com sucesso e recursos desalocados.")
        else:
            print(f"Erro na destruição da rede: Código HTTP {response.status_code} - {response.text}")

    @classmethod
    def create_policy(cls, name: str, protocol: str, bandwidth: float) -> None:
        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.post(f"{cls.BASE_URL}/manage_policy", json=policy_data)


        if response.status_code == 200:
            print("Política criada com sucesso.")
        else:
            print(f"Erro na criação da política: Código HTTP {response.status_code} - {response.text}")


    @classmethod
    def update_policy(cls, name: str, protocol: str, bandwidth: float) -> None:
        policy_data = {"name": name, "protocol": protocol, "bandwidth": bandwidth}
        response = requests.put(f"{cls.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política atualizada com sucesso.")
        else:
            print(f"Erro na atualização da política: Código HTTP {response.status_code} - {response.text}")


    @classmethod
    def remove_policy(cls, protocol: str) -> None:
        policy_data = {"protocol": protocol}
        response = requests.delete(f"{cls.BASE_URL}/manage_policy", json=policy_data)

        if response.status_code == 200:
            print("Política removida com sucesso.")
        else:
            print(f"Erro na remoção da política: Código HTTP {response.status_code} - {response.text}")

    @classmethod
    def show_network_state(cls) -> None:
        response = requests.get(f"{cls.BASE_URL}/get_statistics")
        if response.status_code == 200:
            print("Informações da rede recuperadas com sucesso.")
        else:
            print(f"Erro na recuperação do estado da rede: Código HTTP {response.status_code} - {response.text}")

    @staticmethod
    def show_manual() -> None:
        pass

class Dispatcher:
    @staticmethod
    def dispatch():
        parser = argparse.ArgumentParser(description="Gerenciador de Redes SDN")
        parser.add_argument(
            "action",
            type=str,
            choices=["create_network", "destroy_network", "create_policy", "update_policy", "remove_policy", "show_network_state", "show_manual"],
            help="Escolha a ação a ser executada"
        )

        # Adiciona os parâmetros opcionais conforme necessário
        parser.add_argument("--file", type=str, help="Caminho de um arquivo JSON para criar a rede")
        parser.add_argument("--name", type=str, help="Nome da política para criar ou atualizar")
        parser.add_argument("--protocol", type=str, help="Protocolo da política (ex: HTTP, FTP e RTP)")
        parser.add_argument("--bandwidth", type=float, help="Largura de banda para a política")

        args = parser.parse_args()
        
        # Mapeia o argumento para o método correspondente, passando parâmetros necessários
        action_map = {
            "create_network": lambda: Actions.create_network(args.file),
            "destroy_network": Actions.destroy_network,
            "create_policy": lambda: Actions.create_policy(args.name, args.protocol, args.bandwidth),
            "update_policy": lambda: Actions.update_policy(args.name, args.protocol, args.bandwidth),
            "remove_policy": lambda: Actions.remove_policy(args.protocol),
            "show_network_state": Actions.show_network_state,
            "show_manual": Actions.show_manual
        }

        # Executa o método correspondente
        if args.action in action_map:
            action_map[args.action]()
        else:
            print("Ação desconhecida. Use --help para ver as opções.")

if __name__ == "__main__":
    Dispatcher.dispatch()

