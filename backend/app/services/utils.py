# backend/app/services/utils.py

import socket

HOST = "bus"      # nombre del contenedor bus en Docker Compose
PORT = 5000
PREFIX_LEN = 5

def create_bus_socket() -> socket.socket:
    """Conecta y devuelve un socket al bus."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def send_prefixed(sock: socket.socket, body: str):
    """Envía body con framing [5 dígitos de longitud] + body."""
    prefix = str(len(body)).zfill(PREFIX_LEN)
    sock.sendall((prefix + body).encode())

def recv_all(sock: socket.socket, n: int) -> bytes:
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        buf += chunk
    return buf

def recv_message(sock: socket.socket) -> str:
    """Recibe un mensaje entero (prefijo + payload) y devuelve el payload."""
    raw_pref = recv_all(sock, PREFIX_LEN).decode()
    length = int(raw_pref)
    return recv_all(sock, length).decode()
