import socket
import time

# Configurações do cliente
HOST = '127.0.0.1'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 512

# Gera dados fictícios para envio
DATA = b"A" * (10**6)  # 1 MB de dados

def tcp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.connect((HOST, TCP_PORT))
        print(f"Conectado ao servidor TCP em {HOST}:{TCP_PORT}")
        
        start_time = time.time()
        tcp_socket.sendall(DATA)
        end_time = time.time()
        
        print(f"Dados enviados: {len(DATA)} bytes")
        print(f"Tempo de transmissão (TCP): {end_time - start_time:.2f} segundos")

def udp_client():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        print(f"Enviando dados para o servidor UDP em {HOST}:{UDP_PORT}")
        
        start_time = time.time()
        for i in range(0, len(DATA), BUFFER_SIZE):
            udp_socket.sendto(DATA[i:i+BUFFER_SIZE], (HOST, UDP_PORT))
        udp_socket.sendto(b"END", (HOST, UDP_PORT))  # Sinaliza o fim da transmissão
        end_time = time.time()
        
        print(f"Dados enviados: {len(DATA)} bytes")
        print(f"Tempo de transmissão (UDP): {end_time - start_time:.2f} segundos")

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
