from json import load, JSONDecodeError


class Topology:
    def __init__(self, schema: dict):
        self._schema = schema
        self._is_valid = False

    @property
    def schema(self) -> dict:
        return self._schema

    @property
    def is_valid(self) -> bool:
        return self._is_valid

    def _validate_dps(self) -> tuple[str, bool]:
        if "dps" not in self._schema:
            return ("\"dps\" não encontrado no arquivo de topologia.", False)

        dps = self._schema["dps"]

        if not isinstance(dps, list):
            return ("\"dps\" deve ser do tipo \"list\"", False)

        for dp in dps:
            if not isinstance(dp, dict):
                return ("Tipo não permitido para objeto em \"dps\"", False)

            if "name" not in dp:
                return("Campo \"name\" ausente em objeto de \"dps\"", False)

            try:
                hosts = dp["hosts"]
            except KeyError:
                return("Campo \"hosts\" ausente em objeto de \"dps\"", False)

            if not isinstance(hosts, list):
                return ("\"hosts\" deve ser do tipo \"list\"", False)

            for host in hosts:
                if "name" not in host:
                    return("Campo \"name\" ausente em objeto de \"hosts\"",
                           False)

                if not isinstance(host["name"], str):
                    return("Tipo inválido em \"name\" de objeto em \"hosts\"",
                           False)

                if "vlan" not in host:
                    return("Campo \"vlan\" ausente em objeto de \"hosts\"",
                           False)

                if not isinstance(host["vlan"], str):
                    return("Tipo inválido em \"vlan\" de objeto em \"hosts\"",
                           False)

        return ("", True)

    def _validate_vlans(self) -> tuple[str, bool]:
        if "vlans" not in self._schema:
            return ("\"vlans\" não encontrado no arquivo de topologia.", False)

        vlans = self._schema["vlans"]

        if not isinstance(vlans, list):
            return ("\"vlans\" deve ser do tipo \"list\"", False)

        for vlan in vlans:
            if not isinstance(vlan, dict):
                return ("Tipo não permitido para objeto em \"vlans\"", False)

            if "name" not in vlan:
                return("Campo \"name\" ausente em objeto de \"vlans\"", False)

            if not isinstance(vlan["name"], str):
                return("Tipo inválido em \"name\" de objeto em \"vlans\"",
                       False)

            if "description" not in vlan:
                return("Campo \"description\" ausente em objeto de \"vlans\"",
                       False)

            if not isinstance(vlan["description"], str):
                return("Tipo inválido em \"description\" de objeto em \"vlans\"",
                       False)

        return ("", True)

    def validate(self) -> tuple[str, bool]:
        (err_dps, is_dps_valid) = self._validate_dps()
        if not is_dps_valid:
            return (err_dps, False)

        (err_vlans, is_vlans_valid) = self._validate_vlans()
        if not is_vlans_valid:
            return (err_vlans, False)

        self._is_valid = True

        return ("", True)


class TopologyFactory:
    @staticmethod
    def create_from(config: dict) -> tuple[str, Topology | None]:
        try:
            topo_schema_path = config["topo_schema_path"]
        except KeyError:
            return ("Caminho para arquivo de topologia não encontrado.", None)

        topo_schema = dict()
        try:
            with open(topo_schema_path, "r") as file:
                topo_schema = load(file)
        except FileNotFoundError as err:
            return (str(err), None)
        except JSONDecodeError as err:
            return (str(err), None)

        return ("", Topology(schema=topo_schema))

