import socket
import threading

def handle_connection(client_socket, remote_host, remote_port):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    def forward(source, destination):
        while True:
            data = source.recv(4096)
            if not data:
                break
            destination.sendall(data)

    threading.Thread(target=forward, args=(client_socket, remote_socket), daemon=True).start()
    threading.Thread(target=forward, args=(remote_socket, client_socket), daemon=True).start()

def start_forwarder(local_port, remote_host, remote_port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', local_port))
    server.listen(5)
    print(f"[*] 监视 127.0.0.1:{local_port} => {remote_host}:{remote_port}")
    
    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_connection, args=(client_sock, remote_host, remote_port), daemon=True).start()
