from enum import Enum

class Utils:
    @staticmethod
    def read_file() -> dict:
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

