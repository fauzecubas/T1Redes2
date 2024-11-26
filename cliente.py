import socket
import time

# Configurações do cliente
HOST = '127.0.0.1'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 4096

# Gera dados fictícios para envio
DATA = b"A" * (10**6)  # 1 MB de dados
PACKET_COUNT = (len(DATA) + BUFFER_SIZE - 1) // BUFFER_SIZE  # Número total de pacotes

def save_report(protocol, data_size, duration):
    """Gera um relatório após a transmissão."""
    with open(f"relatorio_cliente_{protocol}.txt", "w") as file:
        file.write(f"Relatório do Cliente ({protocol})\n")
        file.write(f"Tamanho dos dados enviados: {data_size} bytes\n")
        file.write(f"Tempo de transmissão: {duration:.6f} segundos\n")
        file.write(f"Velocidade média: {data_size / duration / (10**6):.2f} MB/s\n")
    print(f"Relatório salvo em 'relatorio_cliente_{protocol}.txt'.")

def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect((HOST, TCP_PORT))
        print(f"Conectado ao servidor TCP em {HOST}:{TCP_PORT}")
        
        start_time = time.perf_counter()
        tcp_socket.sendall(DATA)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        print(f"Dados enviados: {len(DATA)} bytes")
        print(f"Tempo de transmissão (TCP): {duration:.6f} segundos")
        save_report("TCP", len(DATA), duration)

def udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        print(f"Enviando dados para o servidor UDP em {HOST}:{UDP_PORT}")
        
        start_time = time.perf_counter()
        for i in range(PACKET_COUNT):
            packet = i.to_bytes(4, byteorder='big') + DATA[i * BUFFER_SIZE:(i + 1) * BUFFER_SIZE]
            udp_socket.sendto(packet, (HOST, UDP_PORT))
            time.sleep(0.001)
        udp_socket.sendto(b"END", (HOST, UDP_PORT))  # Sinaliza o fim da transmissão
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        print(f"Dados enviados: {len(DATA)} bytes")
        print(f"Tempo de transmissão (UDP): {duration:.6f} segundos")
        save_report("UDP", len(DATA), duration)

if __name__ == "__main__":
    print("Escolha o protocolo para o cliente:")
    print("1. TCP")
    print("2. UDP")
    choice = input("Digite 1 ou 2: ").strip()
    
    if choice == "1":
        tcp_client()
    elif choice == "2":
        udp_client()
    else:
        print("Escolha inválida!")
