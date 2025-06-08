# backend/app/services/utils.py

import socket
from typing import Callable

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
    """Recibe exactamente n bytes del socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        buf += chunk
    return buf

def recv_message(sock: socket.socket) -> str:
    """Recibe un mensaje entero (prefijo + payload) y devuelve solo el payload."""
    raw_pref = recv_all(sock, PREFIX_LEN).decode()
    length = int(raw_pref)
    return recv_all(sock, length).decode()

def serve(service_id: str, handler: Callable[[str], str]):
    """
    Loop genérico de un microservicio:
    1) Anuncia con sinit<service_id>
    2) Espera ack
    3) Repeatedly recibe mensajes, filtra por service_id y delega a handler
    4) Envía la respuesta que devuelve handler
    """
    sock = create_bus_socket()
    send_prefixed(sock, f"sinit{service_id}")
    _ = recv_message(sock)  # ack del bus

    while True:
        msg = recv_message(sock)
        cmd, payload = msg[:len(service_id)], msg[len(service_id):]
        if cmd != service_id:
            continue
        response = handler(payload)
        send_prefixed(sock, response)
