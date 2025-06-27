# Import necessary libraries
import socket
import threading
import os

# Define server IP address, port, buffer size, and log file name
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024
LOG_FILE = "chat_log.txt"

# Save a message to a local chat log file
def log_message(msg):
    with open(LOG_FILE, "a") as log:
        log.write(msg + "\n")

# Receive and display messages or files from the server
# Handles both text messages and file transfers
def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(BUFFER_SIZE).decode()
            if msg.startswith("[FILE]"):
                filename = msg.split(":")[1].strip()
                with open(f"received_{filename}", "wb") as f:
                    while True:
                        data = sock.recv(BUFFER_SIZE)
                        if data.endswith(b"<END>"):
                            f.write(data[:-5])
                            break
                        f.write(data)
                print(f"[Notification] Received file: received_{filename}")
                log_message(f"[Notification] Received file: {filename}")
            else:
                print(msg)
                log_message(msg)
        except:
            print("[ERROR] Connection lost.")
            break

# Read user input and send it to the server
# Detects file commands and sends file content in binary chunks
def send_messages(sock):
    while True:
        msg = input()
        if msg.lower() == 'exit':
            break
        elif msg.startswith("/file"):
            try:
                _, path = msg.split(" ", 1)
                if os.path.exists(path):
                    sock.send(f"[FILE]:{os.path.basename(path)}".encode())
                    with open(path, "rb") as f:
                        while chunk := f.read(BUFFER_SIZE):
                            sock.send(chunk)
                    sock.send(b"<END>")
                    print(f"[Notification] File '{path}' sent.")
                    log_message(f"[Notification] Sent file: {path}")
                else:
                    print("[ERROR] File not found.")
            except ValueError:
                print("[USAGE] /file <filename>")
        else:
            sock.send(msg.encode())
            log_message(f"Me: {msg}")

# Connect to server, enter username, and start send/receive threads
def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    username = input("Enter your username: ")
    client.send(username.encode())

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    send_messages(client)
    client.close()

# Run the client main function when the script is executed
if __name__ == "__main__":
    main()
