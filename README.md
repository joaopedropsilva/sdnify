# SDNIFY

Gerenciador para redes SDN

O sdnify é uma aplicação que estende as funcionalidades de um controlador de redes SDN.

## 1. FUNCIONALIDADES

- Automatização da criação e manutenção de políticas de classificação de pacotes;
- Provisionamento de redes virtuais para testagem de diferentes cenários de rede;
- Reconstrução de caminhos e redirecionamento automático de enlaces congestinados;
- Monitoramento, metrificação e alertas sobre o estado de operação da rede;
- Interface de comando simplificada.

## 2. CONFIGURANDO O GERENCIADOR

Um arquivo de configuração padrão está disponível no formato JSON, definida na raíz do projeto: `config.example.json`. Caso seja necessário o usuário pode criar seu próprio `config.json` (o nome deve ser exatamente este) desde que contenha as mesmas propriedades padrão definidas abaixo.

Propriedades padrão:

- `topo_schema_path`: o caminho do arquivo de topologia da rede virtual a ser instanciada;
- `max_bandwidth`: o limite máximo de banda permitido nos enlaces da rede virtual.

## 3. INTERFACE DE COMANDOS

Uma interface de linha de comando está disponível para disparar as ações implementadas, para utilizá-la é necessário invocar o script `cli.sh` na raíz do projeto. Para detalhes sobre como utilizar cada comando e quais argumentos devem estar presentes execute o script com o parâmetro `--help`.

Uso da interface:

`./cli.sh [args]`

Obtendo ajuda para uso da interface:

`./cli.sh --help`

OBS.: `cli.sh` não é suportado em ambientes windows, para utilizar a interface ative o ambiente virtual e, dentro do diretório raíz do projeto, execute: `python -m src.cli [args]`.

Ações disponíveis pelo gerenciador:

- `virtnet_create`: criar uma rede virtual;
- `virtnet_destroy`: destruir uma rede virtual instanciada;
- `virtnet_status`: exibir o status de operação da rede virtual instanciada;
- `create_policy`: criar uma política de classificação de pacotes;
- `remove_policy`: remover uma política de classificação de pacotes;
- `manual`: acesso ao presente manual de operação; 
- `test`: executar algum arquivo de testes.

## 4. INSTANCIANDO REDES VIRTUAIS

Para trabalhar com redes virtuais é necessário definir a topologia da rede desejada em um arquivo no formato JSON com exatamente a seguinte estrutura (no processo de instanciação essa estrutura é validada e caso esteja incorreta a rede não será instanciada):

```json
{
    "dps": [DP_OBJECT", ...],
    "vlans": [VLAN_OBJECT, ...]
}
```

Propriedades de um `DP_OBJECT`:

- `name`: nome da switch;
- `hosts`: lista de `HOST_OBJECT`.

Propriedades de um `HOST_OBJECT`:

- `name`: nome do host;
- `vlan`: nome da vlan que agrega esse host.

Propriedades de um `VLAN_OBJECT`:

- `name`: nome da vlan;
- `description`: descrição da vlan.

O arquivo de topologia definido deve ter seu caminho especificado no arquivo de configuração do controlador, na propriedade `topo_schema_path`.

Exemplo de topologia: 

```json
{
    "dps": [
        {
            "name": "sw1",
            "hosts": [
                {
                    "name": "h1",
                    "vlan": "test"
                },
                {
                    "name": "h2",
                    "vlan": "test"
                }
            ]
        }
    ],
    "vlans": [
        {
            "name": "test",
            "description": "test vlan"
        }
    ]
}
```

Uma API com os seguintes endpoints estão disponíveis para controle da rede virtual:

- `/virtnet/start`
    Instancia uma rede virtual pré definida no arquivo especificado por topo_schema_path configuração do gerenciador.

    Métodos HTTP permitidos: `POST`
    Payload da requisição: Não é necessário payload.

- `/virtnet/destroy`
    Suspende a operação de uma rede virtual instanciada e desaloca os recursos utilizados.

    Métodos HTTP permitidos: `POST`
    Payload da requisição: Não é necessário payload.

- `/virtnet/status`
    Obtém o status de operação de uma rede virtual instanciada.

    Métodos HTTP permitidos: `GET`
    Payload da requisição: Não é necessário payload.

## 5. POLÍTICAS DE CLASSIFICAÇÃO DE PACOTES

A criação e remoção de políticas de classificação de pacotes está disponível através da interface de linha de comando (idem ao item 3) e através de do endpoint `/manager/manage_policy`.

1. Criando uma nova política:

Método HTTP: `POST`
Payload da requisição:

```json
{
    "data": {
        "traffic_type": TRAFFIC_TYPE,
        "bandwidth": BANDWIDTH
    }
}
```

2. Removendo uma política já criada:

Método HTTP: `DELETE`
Payload da requisição:

```json
{
    "data": {
        "traffic_type": TRAFFIC_TYPE
    }
}
```

- `TRAFFIC_TYPE`: é o tipo de tráfego que a política irá agir sobre. Estão disponíveis os seguintes tipos: `http`, `ftp` e `voip`.
- `BANDWIDTH`: um inteiro maior que 1 e menor que o valor limite definido no arquivo de configuração do gerenciador pela propriedade `max_bandwidth` (idem ao item 2) representa a largura de banda limite que a política vai estabelecer para aquele tipo de tráfego.

## 6. MONITORAMENTO

A coleta e agregação de métricas e disponibilização de alertas é realizada pelo [Prometheus](https://prometheus.io/). A visualização dos dados coletados pode ser feita através de dashboards personalizáveis utilizando o [Grafana](https://grafana.com/). Ambos os serviços disponibilizam interfaces para o usuário.

Acesso às interfaces:

- Prometheus: `http://<host-do-gerenciador>:9090/`
- Grafana: `http://<host-do-gerenciador>:3000/`

