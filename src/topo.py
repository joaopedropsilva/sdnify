class Validator:
    @staticmethod
    def validate_json(data: dict) -> bool:
        try:
            if not isinstance(data.get("hosts"), list):
                raise InvalidTopologyError("Chave 'Hosts' deve ser do tipo list.")
            
            for host in data["hosts"]:
                if not isinstance(host, str):
                    raise InvalidTopologyError("Cada item da lista 'Hosts' deve ser passado como string.")
            
            if not isinstance(data.get("switches"), list):
                raise InvalidTopologyError("Chave 'Switches' deve ser do tipo 'list'.")
            
            for switch in data["switches"]:
                if not isinstance(switch, dict):
                    raise InvalidTopologyError("Chave 'Switches' deve ser composta por uma lista de objetos.")
                if "id" not in switch or not isinstance(switch["id"], str):
                    raise InvalidTopologyError("Objetos da lista 'Switches' devem conter uma chave 'id' do tipo 'string'.")
                if "link" not in switch or not isinstance(switch["link"], list):
                    raise InvalidTopologyError("Objetos da lista 'Switches' devem conter uma lista 'link' representando conexões.")
                
            for link in switch["link"]:
                if not isinstance(link, str):
                    raise InvalidTopologyError("Chave 'link' nos objetos da lista 'switches' deve ser do tipo string.")

            return True

        except InvalidTopologyError as e:
            print(e)
            return False
        
        finally:
            print("Topologia Válida.")

class InvalidTopologyError(Exception):
    def __init__(self, message = "Topologia de rede inválida."):
        super().__init__(message)