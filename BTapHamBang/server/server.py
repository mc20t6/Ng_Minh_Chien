import socket
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.hash_utils import calculate_sha256

HOST = '0.0.0.0'
PORT = 9090
SAVE_DIR = "received_files"
os.makedirs(SAVE_DIR, exist_ok=True)

server = socket.socket()
server.bind((HOST, PORT))
server.listen(5)
print(f"[SERVER] Listening on {HOST}:{PORT}...")

while True:
    conn, addr = server.accept()
    print(f"[SERVER] Connection from {addr}")
    filename = conn.recv(1024).decode()
    conn.send(b'FILENAME RECEIVED')

    file_path = os.path.join(SAVE_DIR, filename)
    with open(file_path, 'wb') as f:
        while True:
            data = conn.recv(4096)
            if not data:
                break
            f.write(data)

    received_hash = conn.recv(1024).decode()
    actual_hash = calculate_sha256(file_path)

    if received_hash == actual_hash:
        print(f"[SERVER] File received intact: {filename}")
    else:
        print(f"[SERVER] Hash mismatch for file: {filename}")

    conn.close()
