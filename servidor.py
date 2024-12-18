import socket
import time
import os
import threading

# Configurações do servidor
HOST = '0.0.0.0'
TCP_PORT = 5000
UDP_PORT = 5001
BUFFER_SIZE = 8192

def save_report(protocol, data_size, duration, lost_packets=None):
    """Gera um relatório após a recepção dos dados."""
    with open(f"relatorio_servidor_{protocol}.txt", "w") as file:
        file.write(f"Relatorio do Servidor ({protocol})\n")
        file.write(f"Tamanho dos dados recebidos: {data_size} bytes\n")
        file.write(f"Tempo de transmissao: {duration:.6f} segundos\n")
        file.write(f"Velocidade media: {data_size / duration / (10**6):.2f} MB/s\n")
        if lost_packets is not None:
            file.write(f"Pacotes perdidos: {lost_packets}\n")
    print(f"Relatório salvo em 'relatorio_servidor_{protocol}.txt'.")

def save_received_file(data, file_name):
    """Salva os dados recebidos no formato original."""
    with open(file_name, "wb") as file:
        file.write(data)
    print(f"Arquivo salvo como '{file_name}'.")

def handle_client(conn, addr):
    """Processa a recepção de dados de um cliente TCP."""
    print(f"Conexão estabelecida com {addr}")
    start_time = time.perf_counter()

    with conn:
        # Receber o nome do arquivo (256 bytes fixos)
        file_name = conn.recv(256).strip().decode('utf-8')
        print(f"Recebendo arquivo: {file_name}")
        
        # Salvar os dados diretamente no arquivo
        with open(file_name, "wb") as file:
            total_received = 0
            while True:
                data = conn.recv(BUFFER_SIZE)
                if not data:
                    break
                file.write(data)
                total_received += len(data)

    end_time = time.perf_counter()

    duration = end_time - start_time
    print(f"\nDados recebidos: {total_received} bytes")
    print(f"Tempo de transmisso (TCP): {duration:.6f} segundos")

    save_report("TCP", total_received, duration)

def tcp_server():
    """Servidor para recepção de dados via TCP, com barra de progresso e suporte a multiplos clientes."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
        tcp_socket.bind((HOST, TCP_PORT))
        tcp_socket.listen(1)
        # print(f"Servidor TCP aguardando conexões na porta {TCP_PORT}...")

        while True:
            try:
                conn, addr = tcp_socket.accept()
                # Inicia uma nova thread para processar o cliente
                threading.Thread(target=handle_client, args=(conn, addr)).start()
            except KeyboardInterrupt:
                print("\nInterrupcao recebida. Encerrando o servidor...")
                break

def udp_server():
    """Servidor para recepção de dados via UDP com envio de ACKs e reordenação de pacotes."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
        udp_socket.bind((HOST, UDP_PORT))
        udp_socket.settimeout(30)  # Timeout ajustado para redes lentas
        # print(f"Servidor UDP aguardando dados na porta {UDP_PORT}...")

        buffer = {}  # Buffer para armazenar pacotes fora de ordem
        received_packets = set()
        start_time = None

        # Receber o nome do arquivo (primeiro pacote)
        file_name, addr = udp_socket.recvfrom(BUFFER_SIZE)
        file_name = file_name.decode('utf-8').strip()
        # print(f"Recebendo arquivo: {file_name}")

        try:
            while True:
                data, addr = udp_socket.recvfrom(BUFFER_SIZE + 4)

                # Identificar pacote de término
                if data == b"END":
                    # print("Pacote de término recebido. Finalizando...")
                    break

                # Registrar o tempo inicial na chegada do primeiro pacote
                if not start_time:
                    start_time = time.perf_counter()

                # Extrair o ID do pacote e os dados
                packet_id = int.from_bytes(data[:4], byteorder='big')
                packet_data = data[4:]

                # Armazenar o pacote se ainda não recebido
                if packet_id not in received_packets:
                    received_packets.add(packet_id)
                    buffer[packet_id] = packet_data

                # Enviar ACK para o cliente
                ack = packet_id.to_bytes(4, byteorder='big')
                udp_socket.sendto(ack, addr)

        except socket.timeout:
            # print("Tempo limite atingido. Nenhum pacote recebido ou comunicação incompleta.")
            return

        end_time = time.perf_counter()
        duration = end_time - start_time

        # Reorganizar pacotes e criar o arquivo completo
        data_received = b"".join(buffer[i] for i in sorted(buffer))
        total_packets = max(received_packets) + 1 if received_packets else 0
        lost_packets = total_packets - len(received_packets)

        print(f"Dados recebidos: {len(data_received)} bytes")
        print(f"Pacotes esperados: {total_packets}, recebidos: {len(received_packets)}, perdidos: {lost_packets}")
        print(f"Tempo de transmissão (UDP): {duration:.6f} segundos")

        # Salvar o arquivo recebido
        save_received_file(data_received, file_name)
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