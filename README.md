# SDNIFY

O `sdnify` é uma aplicação que simplifica e automatiza algumas funcionalidades disponibilizadas pelo controlador [Faucet SDN](faucet.nz).

## 1. Funcionalidades

- Automatização da criação e manutenção de políticas de classificação de pacotes para limitação de tráfego;
- Simplificação no estabelecimento de redundância numa rede, através da feature [`stacking`](https://docs.faucet.nz/en/latest/tutorials/stacking.html);
- Monitoramento e disponibilizção de um dashboard para avaliar a operação da rede;
- Interface de comando simplificada.

Para a testagem de cada funcionalidade a aplicação conta com um ambiente de testagem em containers [`docker`](https://docs.docker.com/get-started/), onde é possível instanciar uma rede virtual utilizando switches [Open vSwich (OVS)](https://www.openvswitch.org/).

## 2. Testando as funcionalidades

### Inicializando o ambiente de teste

Para testar cada funcionalidade é necessário inicializar o ambiente `docker` através da execução dos seguintes scripts na raíz do projeto:
1. `setup.sh` para fazer as instalações necessárias e criar a imagem do container de testes (É necessário conexão com a Internet para a instalação dos pacotes que vão ser utilizados no container);
2. `run-test-env.sh` para executar o container de testes.

> Esse projeto foi prototipado para ser executado em ambientes `Linux` e depende da instalação de dependências como: [Docker Engine](https://docs.docker.com/engine/), [Docker Compose](https://docs.docker.com/compose/) e [Python 3.10](https://www.python.org/downloads/release/python-31016/).

### Utilizando arquivos exemplos prontos

O diretório `examples` conta com diversos arquivos `.sh` e `.json`, que definem exemplos prontos para serem executados para cada funcionalidade da aplicação. Cada exemplo é definido por um nome, ou seja:
- `simple-network` (instanciação de uma rede com dois hosts e uma switch e execução de interação entre os hosts);
- `rate-limits` (imposição de limitações na banda para tráfegos simulados);
- `stacking` (aplicação de uma rede com três switches interligadas e configurações de redundância).

Para executar um exemplo garanta que você já esteja conectado no container de testes. Em seguida utilize a interface de linha de comando `sdnify` seguida do nome do exemplo desejado.

```
sdnify <nome-do-exemplo>
```
### Utilizando um exemplo definido pelo usuário

TBD.

## 3. Monitoramento e acesso ao dashboard

A coleta e agregação de métricas e disponibilização de alertas é realizada pelo [Prometheus](https://prometheus.io/). A visualização dos dados coletados pode ser feita através de dashboards personalizáveis utilizando o [Grafana](https://grafana.com/). Ambos os serviços disponibilizam interfaces para o usuário.

Acesso às interfaces:

- Prometheus: `http://localhost:9090/`
- Grafana: `http://localhost:3000/`

