from enum import Enum

from pathlib import Path

import json
import requests

class Utils:
    @staticmethod
    def read_file(file_path: str) -> dict:
        try:
            file_path = Path(file_path).resolve()
        
            if not file_path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")
        
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
                
            return data
        
        except FileNotFoundError as e:
            print(e)
            return None
        
        finally:
            print("Operação de leitura do arquivo concluída.")

class topologyValidator:
    @staticmethod
    def validate_json(data: dict) -> bool:
        try:
            if not isinstance(data.get("hosts"), list):
                raise invalidTopologyError("Chave 'Hosts' deve ser do tipo list.")
            
            for host in data["hosts"]:
                if not isinstance(host, str):
                    raise invalidTopologyError("Cada item da lista 'Hosts' deve ser passado como string.")
            
            if not isinstance(data.get("switches"), list):
                raise invalidTopologyError("Chave 'Switches' deve ser do tipo 'list'.")
            
            for switch in data["switches"]:
                if not isinstance(switch, dict):
                    raise invalidTopologyError("Chave 'Switches' deve ser composta por uma lista de objetos.")
                if "id" not in switch or not isinstance(switch["id"], str):
                    raise invalidTopologyError("Objetos da lista 'Switches' devem conter uma chave 'id' do tipo 'string'.")
                if "link" not in switch or not isinstance(switch["link"], list):
                    raise invalidTopologyError("Objetos da lista 'Switches' devem conter uma lista 'link' representando conexões.")
                
            for link in switch["link"]:
                if not isinstance(link, str):
                    raise invalidTopologyError("Chave 'link' nos objetos da lista 'switches' deve ser do tipo string.")

            return True

        except invalidTopologyError as e:
            print(e)
            return False
        
        finally:
            print("Topologia Válida.")

class invalidTopologyError(Exception):
    def __init__(self, message = "Topologia de rede inválida."):
        super().__init__(message)

class RoutineResults():
    def __init__(self, status: bool = False, err_reason: str = "", payload = None):
        self.__status = status
        self.__err_reason = err_reason
        self.__payload = payload

    @property
    def status(self):
        return self.__status

    @property
    def err_reason(self):
        return self.__err_reason

    @property
    def payload(self):
        return self.__payload

class Display:
    @staticmethod
    def inform() -> None:
        pass

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

class PolicyTypes(Enum):
    VOIP = 1,
    HTTP = 2,
    FTP = 3

