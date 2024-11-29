import socket
import time
import os

# Configurações do cliente
HOST = '127.0.0.1'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 4096

def save_report(protocol, data_size, duration):
    """Gera um relatório após a transmissão."""
    with open(f"relatorio_cliente_{protocol}.txt", "w") as file:
        file.write(f"Relatório do Cliente ({protocol})\n")
        file.write(f"Tamanho dos dados enviados: {data_size} bytes\n")
        file.write(f"Tempo de transmissão: {duration:.6f} segundos\n")
        file.write(f"Velocidade média: {data_size / duration / (10**6):.2f} MB/s\n")
    print(f"Relatório salvo em 'relatorio_cliente_{protocol}.txt'.")

def tcp_client(file_path):
    """Envia um arquivo usando TCP."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect((HOST, TCP_PORT))
        print(f"Conectado ao servidor TCP em {HOST}:{TCP_PORT}")

        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path).encode('utf-8')

        # Enviar o nome do arquivo (fixo em 256 bytes, preenchido com espaços se necessário)
        tcp_socket.sendall(file_name.ljust(256))

        # Enviar os dados do arquivo
        with open(file_path, 'rb') as file:
            start_time = time.perf_counter()
            tcp_socket.sendall(file.read())
            end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"Arquivo enviado: {file_path}")
        print(f"Tamanho do arquivo: {file_size} bytes")
        print(f"Tempo de transmissão (TCP): {duration:.6f} segundos")
        save_report("TCP", file_size, duration)

def udp_client(file_path):
    """Envia um arquivo usando UDP com retransmissão e timeout adaptativo."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        print(f"Enviando arquivo para o servidor UDP em {HOST}:{UDP_PORT}")

        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path).encode('utf-8')
        total_packets = (file_size + BUFFER_SIZE - 1) // BUFFER_SIZE
        acked_packets = set()

        # Enviar o nome do arquivo como primeiro pacote
        udp_socket.sendto(file_name, (HOST, UDP_PORT))

        # Inicializar estimadores
        estimated_rtt = 0.1  # RTT estimado inicial em segundos
        dev_rtt = 0.05       # Desvio padrão inicial
        alpha = 0.125        # Fator de suavização para EstimatedRTT
        beta = 0.25          # Fator de suavização para DevRTT

        with open(file_path, 'rb') as file:
            start_time = time.perf_counter()
            packets = []
            for i in range(total_packets):
                chunk = file.read(BUFFER_SIZE)
                packet = i.to_bytes(4, byteorder='big') + chunk
                packets.append(packet)

            while len(acked_packets) < total_packets:
                for i, packet in enumerate(packets):
                    if i not in acked_packets:
                        udp_socket.sendto(packet, (HOST, UDP_PORT))
                        send_time = time.perf_counter()

                        try:
                            ack_data, _ = udp_socket.recvfrom(8)
                            receive_time = time.perf_counter()
                            sample_rtt = receive_time - send_time

                            # Atualizar estimadores
                            estimated_rtt = (1 - alpha) * estimated_rtt + alpha * sample_rtt
                            dev_rtt = (1 - beta) * dev_rtt + beta * abs(sample_rtt - estimated_rtt)
                            timeout_interval = estimated_rtt + 4 * dev_rtt
                            udp_socket.settimeout(timeout_interval)

                            ack_id = int.from_bytes(ack_data[:4], byteorder='big')
                            acked_packets.add(ack_id)
                            if len(acked_packets) == total_packets:
                                break

                        except socket.timeout:
                            print(f"Timeout de {udp_socket.gettimeout():.10f} s. Retransmitindo pacotes não confirmados...")

            udp_socket.sendto(b"END", (HOST, UDP_PORT))
            end_time = time.perf_counter()

        duration = end_time - start_time
        print(f"Arquivo enviado: {file_path}")
        print(f"Tamanho do arquivo: {file_size} bytes")
        print(f"Tempo de transmissão (UDP): {duration:.6f} segundos")
        save_report("UDP", file_size, duration)


if __name__ == "__main__":
    print("Escolha o protocolo para o cliente:")
    print("1. TCP")
    print("2. UDP")
    choice = input("Digite 1 ou 2: ").strip()
    
    file_path = input("Digite o caminho do arquivo para envio: ").strip()
    if not os.path.isfile(file_path):
        print("Arquivo não encontrado!")
    elif choice == "1":
        tcp_client(file_path)
    elif choice == "2":
        udp_client(file_path)
    else:
        print("Escolha inválida!")