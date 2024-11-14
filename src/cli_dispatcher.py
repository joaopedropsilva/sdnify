import argparse
from network import ActionDirector

def cli_dispatcher():
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
        "create_network": lambda: ActionDirector.create_network(args.file),
        "destroy_network": ActionDirector.destroy_network,
        "create_policy": lambda: ActionDirector.create_policy(args.name, args.protocol, args.bandwidth),
        "update_policy": lambda: ActionDirector.update_policy(args.name, args.protocol, args.bandwidth),
        "remove_policy": lambda: ActionDirector.remove_policy(args.protocol),
        "show_network_state": ActionDirector.show_network_state,
        "show_manual": ActionDirector.show_manual
    }

    # Executa o método correspondente
    if args.action in action_map:
        action_map[args.action]()
    else:
        print("Ação desconhecida. Use --help para ver as opções.")

if __name__ == "__main__":
    cli_dispatcher()

