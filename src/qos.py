from typing import List

from information import PolicyTypes, RoutineResults

class Policy:
    def __init__(self, name: str, traffic_type: PolicyTypes, bandwidth_reserved: int):
        self.name = name
        self.traffic_type = traffic_type
        self.bandwidth_reserved = bandwidth_reserved

class FlowManager:
    def __init__(self):
        self.__config: dict = {}
        self.policies: List[Policy] = []

    def __validate(self, policy: Policy) -> RoutineResults:
        try:
            errors = []

            if not policy.name:
                errors.append("Nome de política inválido.")
            
            if not isinstance(policy.traffic_type, PolicyTypes):
                errors.append("Tipo de tráfego fornecido é inválido.")
            
            if not (0 < policy.bandwidth_reserved <= 1000):
                errors.append("Largura de banda reservada deve estar entre 1 e 100 Mbps.")

            if errors:
                return RoutineResults(status=False, err_reason="; ".join(errors))
            
        except Exception as e:
            return RoutineResults(status=False, err_reason="Erro de validação: {str(e)}")
        
        finally:
            print("Política validada com sucesso.")

    def __init_framework_config(self) -> RoutineResults:
        # inicializa o arquivo de config do controlador
        pass

    def __update_tables(self, policy: Policy, operation : str) -> RoutineResults:
        # altera o arquivo de config do controlador para lidar
        # com uma nova política ou com redirecionamento de tráfego

     # criar a estrutura de regra com base na política
        rule = self.__create_rule(policy)

        if operation == "create":
            # Verifica se a política já existe
            if any(p.traffic_type == policy.traffic_type for p in self.policies):
                return RoutineResults(
                    status=False,
                    err_reason=f"Política de tráfego {policy.traffic_type} já existe. Abortando a operação de criacao."
                )
            # adiciona a nova política
            self.policies.append(policy)

            # Atualiza o dicionário de configuração
            if f"{policy.traffic_type}-traffic" not in self.__config:
                self.__config[f"{policy.traffic_type}-traffic"] = []

            self.__config[f"{policy.traffic_type}-traffic"].append(rule)

            # Simula a escrita no arquivo acls.yaml
            self.__write_config()

            return RoutineResults(
                status=True,
                payload=f"Política de tráfego {policy.traffic_type} criada com sucesso."
            )

        elif operation == "update":
            # Procura pela política existente e atualiza
            for existing_policy in self.policies:
                if existing_policy.traffic_type == policy.traffic_type:
                    existing_policy.bandwidth_reserved = policy.bandwidth_reserved

                    # Atualiza a configuração
                    self.__config[f"{policy.traffic_type}-traffic"] = [rule]

                    # Simula a escrita no arquivo acls.yaml
                    self.__write_config()

                    return RoutineResults(
                        status=True,
                        payload=f"Política de tráfego {policy.traffic_type} atualizada com sucesso."
                    )

            return RoutineResults(
                status=False,
                err_reason=f"Política de tráfego {policy.traffic_type} não encontrada para atualização."
            )

        elif operation == "delete":
            # Remove a política da lista e do arquivo de configuração
            self.policies = [p for p in self.policies if p.traffic_type != policy.traffic_type]

            if f"{policy.traffic_type}-traffic" in self.__config:
                del self.__config[f"{policy.traffic_type}-traffic"]

            # Simula a escrita no arquivo acls.yaml
            self.__write_config()

            return RoutineResults(
                status=True,
                payload=f"Política de tráfego {policy.traffic_type} removida com sucesso."
            )

        else:
            return RoutineResults(
                status=False,
                err_reason="Operação desconhecida. Use 'create', 'update' ou 'delete'."
            )
        

    def __create_rule(self, policy: Policy):
        """
        Cria a regra de tráfego baseada na política.
        :param policy: A política que define a regra de tráfego.
        :return: A regra gerada.
        """
        # Criação de regra genérica com base no tipo de tráfego
        rule = {
            "dl_type": "0x800",  # enderecos IPv4 (exemplo genérico)
            "nw_proto": 17 if policy.traffic_type == PolicyTypes.VOIP else 6,  # UDP (VoIP) ou TCP (HTTP e FTP)
            "tcp_dst": 80 if policy.traffic_type != PolicyTypes.VOIP else None,  # Porta padrao para o HTTP e FTP
            "udp_dst": 53 if policy.traffic_type == PolicyTypes.VOIP else None,  # Porta padrao UDP para o VoIP
            "actions": {
                "allow": 1,  # Permitir
                "set_fields": [
                    {"bandwidth_percent": policy.bandwidth_reserved}  # Percentual de banda reservado
                ]
            }
        }
        return rule

    def __write_config(self):
        """
        Simula a escrita no arquivo de configuração (acls.yaml).
        """
        print(f"Arquivo de configuração atualizado: {self.__config}")

    def __process_alerts(self) -> RoutineResults:
        # recebe o alerta do monitor
        # chama redirect_traffic se necessário
        pass

    def redirect_traffic(self) -> RoutineResults:
        pass

    def create(self, policy: Policy) -> RoutineResults:
        try:
            validation = self.__validate(policy)

            if not validation.status == False:
                return validation
            
            self.policies.append(policy)

            update = self.__update_tables()
            
            if update.status == False:
                self.policies.remove(policy)
                return update
            
            return RoutineResults(status=True, payload="Política criada com sucesso.")
        
        except Exception as e:
            print(f"Erro ao criar política: {e}")
            return RoutineResults(status=False, err_reason=str(e))
        
        finally:
            print("Operação de criação de política finalizada.")

    def update(self, policy: Policy) -> RoutineResults:
        pass

    def remove(self, policy: Policy) -> RoutineResults:
        pass


