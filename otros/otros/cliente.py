# cliente.py
import socket

HOST = 'localhost'
BUS_PORT = 5000
PREFIX_LEN = 5

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        data += chunk
    return data

def enviar_transaccion(service_id, payload):
    with socket.socket() as s:
        print(f"[CLIENT] Conectando al bus {HOST}:{BUS_PORT}…")
        s.connect((HOST, BUS_PORT))
        print(f"[CLIENT] Conexión establecida")

        body = service_id + payload
        msg = str(len(body)).zfill(PREFIX_LEN) + body
        print(f"[CLIENT] Enviando: {msg}")
        s.sendall(msg.encode())

        raw_pref = recv_all(s, PREFIX_LEN)
        length = int(raw_pref.decode())
        resp_body = recv_all(s, length).decode()
        print(f"[CLIENT] Respuesta recibida: {resp_body}")

if __name__ == '__main__':
    enviar_transaccion('sumar', '10-3')
    enviar_transaccion('resta', '10-3')
