# Import necessary libraries
import socket
import threading

# Define server IP address, port, and buffer size
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024

# Dictionary to store connected clients and their usernames
clients = {}

# Send messages or files to all connected clients except the sender
def broadcast(data, sender_socket, is_binary=False):
    for client in clients:
        if client != sender_socket:
            try:
                if is_binary:
                    client.sendall(data)
                else:
                    client.send(data)
            except:
                client.close()
                del clients[client]

# Handle communication with an individual client
# Receives username, routes messages, and manages file transfers
def handle_client(client_socket):
    try:
        username = client_socket.recv(BUFFER_SIZE).decode()
        clients[client_socket] = username
        print(f"[+] {username} is connected.")
        broadcast(f"{username} has joined the chat room.".encode(), client_socket)

        while True:
            msg = client_socket.recv(BUFFER_SIZE)
            if not msg:
                break

            if msg.startswith(b"[FILE]:"):
                filename = msg.decode().split(":")[1]
                broadcast(msg, client_socket)
                while True:
                    data = client_socket.recv(BUFFER_SIZE)
                    broadcast(data, client_socket, is_binary=True)
                    if data.endswith(b"<END>"):
                        break
                print(f"[Notification] File '{filename}' transferred.")
            else:
                broadcast(f"{clients[client_socket]}: ".encode() + msg, client_socket)
    except:
        pass
    finally:
        print(f"[-] {clients[client_socket]} is disconnected.")
        broadcast(f"{clients[client_socket]} has left the chat.".encode(), client_socket)
        client_socket.close()
        del clients[client_socket]

# Start the server, listen for connections, and spawn threads for clients
def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"[SERVER] Hosting on {HOST}:{PORT}")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()
# Run the server when the script is executed directly
if __name__ == "__main__":
    start_server()
