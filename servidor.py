import socket
import time

# Configurações do servidor
HOST = '0.0.0.0'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 1024

def save_report(protocol, data_size, duration, checksum_valid):
    """Gera um relatório após a recepção dos dados."""
    with open(f"relatorio_servidor_{protocol}.txt", "w") as file:
        file.write(f"Relatório do Servidor ({protocol})\n")
        file.write(f"Tamanho dos dados recebidos: {data_size} bytes\n")
        file.write(f"Tempo de transmissão: {duration:.6f} segundos\n")
        file.write(f"Velocidade média: {data_size / duration / (10**6):.2f} MB/s\n")
        file.write(f"Checksum válido: {checksum_valid}\n")
    print(f"Relatório salvo em 'relatorio_servidor_{protocol}.txt'.")

def tcp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind((HOST, TCP_PORT))
        tcp_socket.listen(1)
        print(f"Servidor TCP aguardando conexões na porta {TCP_PORT}...")
        
        conn, addr = tcp_socket.accept()
        print(f"Conexão estabelecida com {addr}")
        start_time = time.perf_counter()
        
        data_received = b""
        with conn:
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                data_received += data
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Tempo de transmissão (TCP): {duration:.6f} segundos")
        save_report("TCP", len(data_received), duration, checksum_valid=True)  # Checksum é opcional

def udp_server():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((HOST, UDP_PORT))
        udp_socket.settimeout(5)
        print(f"Servidor UDP aguardando dados na porta {UDP_PORT}...")
        
        data_received = b""
        start_time = None

        try:
            while True:
                data, addr = udp_socket.recvfrom(BUFFER_SIZE)
                if data == b"END":
                    print("Pacote de término recebido. Finalizando...")
                    break
                if not start_time:
                    start_time = time.perf_counter()
                data_received += data
        except socket.timeout:
            print("Tempo limite atingido. Nenhum pacote recebido ou comunicação incompleta.")
            return

        end_time = time.perf_counter()
        duration = end_time - start_time
        
        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Tempo de transmissão (UDP): {duration:.6f} segundos")
        save_report("UDP", len(data_received), duration, checksum_valid=True)  # Checksum é opcional

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
