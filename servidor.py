import socket
import time

# Configurações do servidor
HOST = '0.0.0.0'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 1024

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind((HOST, TCP_PORT))
        tcp_socket.listen(1)
        print(f"Servidor TCP aguardando conexões na porta {TCP_PORT}...")
        
        conn, addr = tcp_socket.accept()
        print(f"Conexão estabelecida com {addr}")
        start_time = time.time()
        
        with conn:
            data_received = b""
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                data_received += data
        end_time = time.time()
        
        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Tempo de transmissão (TCP): {end_time - start_time:.2f} segundos")

def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((HOST, UDP_PORT))
        print(f"Servidor UDP aguardando dados na porta {UDP_PORT}...")
        
        data_received = b""
        start_time = time.time()
        while True:
            data, addr = udp_socket.recvfrom(BUFFER_SIZE)
            if data == b"END":
                break
            data_received += data
        end_time = time.time()
        
        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Tempo de transmissão (UDP): {end_time - start_time:.2f} segundos")

if __name__ == "__main__":
    print("Escolha o protocolo para o servidor:")
    print("1. TCP")
    print("2. UDP")
    choice = input("Digite 1 ou 2: ").strip()
    
    if choice == "1":
        tcp_server()
    elif choice == "2":
        udp_server()
    else:
        print("Escolha inválida!")
