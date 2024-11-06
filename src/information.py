from enum import Enum
import json

import requests

class Utils:
    @staticmethod
    def read_file(source: str) -> dict:
        if source.startswith("http://") or source.startswith("https://"):
            return requests.get(source).json()
        else:
            with open(source, "r", encoding="utf-8") as file:
                return json.load(file)
    
    @staticmethod
    def validate_json_topology(data: dict) -> bool:
        if "hosts" not in data or "switches" not in data:
            raise InvalidTopologyError() 

        if not isinstance(data["hosts"], list):
            raise InvalidTopologyError()
        if not all(isinstance(host,str) for host in data["hosts"]):
            raise InvalidTopologyError()
        pass        

        if not isinstance(data["switches"], list):
            raise InvalidTopologyError()
        pass
        
        for switch in data["switches"]:
            if not isinstance(switch, dict):
                raise InvalidTopologyError()
            pass

            if "id" not in switch or "links" not in switch:
                raise InvalidTopologyError()
            pass 

            if not isinstance(switch["id"], str):
                raise InvalidTopologyError()
            pass

            if not isinstance(switch["links"], list):
                raise InvalidTopologyError()
            pass

            if not all(isinstance(link, str) for link in switch["links"]):
                raise InvalidTopologyError()
            pass

        return True

class InvalidTopologyError(Exception):
    """
    Exceção personalizada para erros de validação da topologia definida no arquivo JSON
    """
    pass

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

