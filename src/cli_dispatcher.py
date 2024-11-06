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
    
    args = parser.parse_args()
    
    # Mapeia o argumento para o método correspondente
    action_map = {
        "create_network": ActionDirector.create_network,
        "destroy_network": ActionDirector.destroy_network,
        "create_policy": ActionDirector.create_policy,
        "update_policy": ActionDirector.update_policy,
        "remove_policy": ActionDirector.remove_policy,
        "show_network_state": ActionDirector.show_network_state,
        "show_manual": ActionDirector.show_manual,
    }
    
    # Executa o método correspondente
    if args.action in action_map:
        action_map[args.action]()
    else:
        print("Ação desconhecida. Use --help para ver as opções.")

if __name__ == "__main__":
    cli_dispatcher()
