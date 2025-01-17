from json import load
from pathlib import Path


class NetConfigValidator:
    @staticmethod
    def _read_from(path: str) -> None:
        if not Path(path).exists():
            raise FileNotFoundError("netconfig.json not found!")

        with open(Path(path).resolve(), "r") as file:
            return load(file)

    def __init__(self, netconfig_path: str):
        self._netconfig = self._read_from(path=netconfig_path)

    def _validate_stacks_from(self, dp: dict) -> tuple[str, bool]:
        try:
            stack_definitions = dp["stack_definitions"]
        except KeyError:
            return "Campo \"stack_definitions\" ausente em objeto de \"dps\"", False

        if not isinstance(stack_definitions, list):
            return "\"stack_definitions\" deve ser do tipo \"list\"", False

        for stack in stack_definitions:
            if "description" not in stack:
                return "Campo \"description\" ausente em objeto de \"stack_definitions\"", False

            if not isinstance(stack["description"], str):
                return "Tipo inválido em \"description\" de objeto em \"stack_definitions\"", False

            if "dp" not in stack:
                return "Campo \"dp\" ausente em objeto de \"stack_definitions\"", False

            if not isinstance(stack["dp"], str):
                return "Tipo inválido em \"dp\" de objeto em \"stack_definitions\"", False

            if "port" not in stack:
                return "Campo \"port\" ausente em objeto de \"stack_definitions\"", False

            if not isinstance(stack["port"], int):
                return "Tipo inválido em \"port\" de objeto em \"stack_definitions\"", False

        return "", True

    def _validate_hosts_from(self, dp: dict) -> tuple[str, bool]:
        try:
            hosts = dp["hosts"]
        except KeyError:
            return "Campo \"hosts\" ausente em objeto de \"dps\"", False

        if not isinstance(hosts, list):
            return "\"hosts\" deve ser do tipo \"list\"", False

        for host in hosts:
            if "name" not in host:
                return "Campo \"name\" ausente em objeto de \"hosts\"", False

            if not isinstance(host["name"], str):
                return "Tipo inválido em \"name\" de objeto em \"hosts\"", False

            if "vlan" not in host:
                return "Campo \"vlan\" ausente em objeto de \"hosts\"", False

            if not isinstance(host["vlan"], str):
                return "Tipo inválido em \"vlan\" de objeto em \"hosts\"", False

        return "", True

    def _validate_datapaths(self) -> tuple[str, bool]:
        if "dps" not in self._schema:
            return "\"dps\" não encontrado no arquivo de topologia.", False

        dps = self._schema["dps"]

        if not isinstance(dps, list):
            return "\"dps\" deve ser do tipo \"list\"", False

        for dp in dps:
            if not isinstance(dp, dict):
                return "Tipo não permitido para objeto em \"dps\"", False

            if "name" not in dp:
                return "Campo \"name\" ausente em objeto de \"dps\"", False

            (err_hosts, are_hosts_valid) = self._validate_hosts_from(dp=dp)
            if not are_hosts_valid:
                return err_hosts, False

            (err_stacks, are_stacks_valid) = self._validate_stacks_from(dp=dp)
            if not are_stacks_valid:
                return err_stacks, False

        return ("", True)

    def validate(self) -> None:
        (err_dps, is_dps_valid) = self._validate_datapaths()
        if not is_dps_valid:
            raise Exception(f"invalid netconfig.json: {err_dps}")

