from flask import Flask
from pathlib import Path
from json import load


class File:
    @staticmethod
    def read_json_from(filepath: str) -> dict:
        try:
            path = Path(filepath)
        
            if not path.exists():
                raise FileNotFoundError(f"Arquivo não encontrado: {path}")
        
            with open(path, "r", encoding="utf-8") as file:
                data = load(file)
                
            return data
        
        except FileNotFoundError:
            return {}

class Api:
    app = Flask(__name__)

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

