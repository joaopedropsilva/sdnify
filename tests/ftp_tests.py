from mininet.net import Mininet
from src.data import NetworkBuilder, Error
from src.utils import File
from time import sleep

class Network:
    _simple_topo = {
        "hosts": ["h1", "h2"],
        "switches": [
            {
                "id": "sw1",
                "links": ["h1", "h2"]
            }
        ]
    }

    @classmethod
    def full_build_network_and_monitor_bandwidth(cls) -> None:
        builder = NetworkBuilder(topo_schema_path=File.get_config()["topo_schema_path"])
        (build_result, net) = builder.build_network()

        if isinstance(build_result, Error):
            raise Exception(build_result.value)
        
        try:
            net.start()
            print("Rede virtual instanciada com sucesso.")

            print("Verificando conexões na rede com pingAll.")
            net.pingAll()

            print("Configurando e monitorando tráfego FTP entre os hosts.")
            cls._configure_ftp_and_monitor_bandwidth(net)  # Corrigido: chamada do método estático
        finally:
            print("Rede virtual finalizada.")
            net.stop()

    @staticmethod
    def _configure_ftp_and_monitor_bandwidth(net: Mininet) -> None:
        h1, h2 = net.get('h1', 'h2')

        print("Iniciando servidor FTP no host h1.")
        h1.cmd('service vsftpd restart')

        print("Criando arquivo texto de teste para tráfego FTP.")
        h1.cmd('echo "Hello World" > /tmp/testfile.txt')  # Corrigido: diretório padrão para temporários

        print("Iniciando iperf no modo servidor no host h1.")
        h1.cmd('iperf -s &')

        print("Iniciando cliente FTP no host h2.")
        h2.cmd(f'ftp -n {h1.IP()} <<EOF\nuser anonymous\nbinary\nget /tmp/testfile.txt\nquit\nEOF')
        print("Arquivo teste transferido do host h1 para o host h2.")

        sleep(3)

        print("Iniciando iperf no modo cliente no host h2.")
        print("Monitorando largura de banda para tráfego FTP gerado. (Ctrl + C para encerrar o teste).")

        try:
            with h2.popen(f'iperf -c {h1.IP()} -b 100Mbit -t 10 -i 1') as process:
                for line in process.stdout: #process.stdout é a saída padrão do comando iperf executado no host h2
                    print(line.strip()) #strip() remove qq espaço em branco ou quebra de linha 
        except KeyboardInterrupt:
            print("Teste interrompido pelo usuário.")
        finally:
            print("Finalizando servidor iperf e serviço FTP.")
            h1.cmd('kill %iperf')
            h1.cmd('killall vsftpd')

if __name__ == "__main__":
    Network.full_build_network_and_monitor_bandwidth()
