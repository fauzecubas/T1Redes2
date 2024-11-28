import socket
import time
import os

# Configurações do servidor
HOST = '0.0.0.0'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 4096

def save_report(protocol, data_size, duration, lost_packets=None):
    """Gera um relatório após a recepção dos dados."""
    with open(f"relatorio_servidor_{protocol}.txt", "w") as file:
        file.write(f"Relatório do Servidor ({protocol})\n")
        file.write(f"Tamanho dos dados recebidos: {data_size} bytes\n")
        file.write(f"Tempo de transmissão: {duration:.6f} segundos\n")
        file.write(f"Velocidade média: {data_size / duration / (10**6):.2f} MB/s\n")
        if lost_packets is not None:
            file.write(f"Pacotes perdidos: {lost_packets}\n")
    print(f"Relatório salvo em 'relatorio_servidor_{protocol}.txt'.")

def save_received_file(data, protocol):
    """Salva os dados recebidos em um arquivo."""
    file_path = f"arquivo_recebido_{protocol}.bin"
    with open(file_path, "wb") as file:
        file.write(data)
    print(f"Arquivo salvo como '{file_path}'.")

def tcp_server():
    """Servidor para recepção de dados via TCP."""
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
        
        save_received_file(data_received, "TCP")
        save_report("TCP", len(data_received), duration)

def udp_server():
    """Servidor para recepção de dados via UDP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((HOST, UDP_PORT))
        udp_socket.settimeout(10)
        print(f"Servidor UDP aguardando dados na porta {UDP_PORT}...")
        
        data_received = b""
        received_packets = set()
        start_time = None

        try:
            while True:
                data, addr = udp_socket.recvfrom(BUFFER_SIZE)
                if data == b"END":
                    print("Pacote de término recebido. Finalizando...")
                    break
                if not start_time:
                    start_time = time.perf_counter()
                packet_id = int.from_bytes(data[:4], byteorder='big')
                received_packets.add(packet_id)
                data_received += data[4:]
        except socket.timeout:
            print("Tempo limite atingido. Nenhum pacote recebido ou comunicação incompleta.")
            return

        end_time = time.perf_counter()
        duration = end_time - start_time

        total_packets = max(received_packets) + 1 if received_packets else 0
        lost_packets = total_packets - len(received_packets)
        
        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Pacotes esperados: {total_packets}, recebidos: {len(received_packets)}, perdidos: {lost_packets}")
        print(f"Tempo de transmissão (UDP): {duration:.6f} segundos")
        
        save_received_file(data_received, "UDP")
        save_report("UDP", len(data_received), duration, lost_packets)

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
