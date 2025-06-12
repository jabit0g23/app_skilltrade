#!/usr/bin/env python3
import argparse
import socket
import sys


"""
Testear el servicio de usuario:

python test_cliente.py USREG "alice;alice@ejemplo.com;secret123"
python test_cliente.py USLOG "alice@ejemplo.com;secret123"
python test_cliente.py USGET "2"
python test_cliente.py USUPD "2;AliceWonder;alice.wonder@ejemplo.com;newpass456"
python test_cliente.py USGET "2"


Testear el servicio de publicaciones:

python test_cliente.py PBNCR "1;oferta;Desarrollo de API en Python;2;dev,backend"
python test_cliente.py PBLST "oferta;API"
python test_cliente.py PBGET "5"
python test_cliente.py PBDEL "1;5"
python test_cliente.py PBGET "5"

"""

HOST = "localhost"   # o "bus" si ejecutas dentro de otro contenedor
PORT = 5000
PREFIX_LEN = 5

def recv_all(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        buf += chunk
    return buf

def enviar_transaccion(service_id: str, payload: str):
    body = service_id + payload
    prefix = str(len(body)).zfill(PREFIX_LEN)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"> Conectado al bus {HOST}:{PORT}")
        msg = prefix + body
        print(f"> Enviando → {msg}")
        s.sendall(msg.encode())

        # recibimos el prefijo de la respuesta
        raw_pref = recv_all(s, PREFIX_LEN).decode()
        length = int(raw_pref)
        # ahora el cuerpo
        resp = recv_all(s, length).decode()
        print(f"< Recibido ← {resp}")
        return resp

def main():
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el bus SOA"
    )
    parser.add_argument("service", help="Código de servicio (p.ej. USREG, USLOG, PBNCR...)")
    parser.add_argument("data", help="Payload para el servicio (sin prefijo)")
    args = parser.parse_args()

    try:
        enviar_transaccion(args.service, args.data)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
