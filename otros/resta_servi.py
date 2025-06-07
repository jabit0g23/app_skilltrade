# servicio_resta.py
import socket

HOST = 'localhost'
BUS_PORT = 5000
PREFIX_LEN = 5
SERVICE_NAME = 'resta'

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        data += chunk
    return data

def main():
    with socket.socket() as s:
        print(f"[{SERVICE_NAME}] Conectando al bus {HOST}:{BUS_PORT}…")
        s.connect((HOST, BUS_PORT))
        print(f"[{SERVICE_NAME}] Conexión establecida")

        # Anuncio
        init = 'sinit' + SERVICE_NAME
        packet = str(len(init)).zfill(PREFIX_LEN) + init
        print(f"[{SERVICE_NAME}] Enviando anuncio: {packet}")
        s.sendall(packet.encode())

        # Recibo ack
        try:
            raw_pref = recv_all(s, PREFIX_LEN)
            ack_len = int(raw_pref.decode())
            ack_body = recv_all(s, ack_len).decode()
            print(f"[{SERVICE_NAME}] Ack recibido: {ack_body}")
        except Exception as e:
            print(f"[{SERVICE_NAME}] Error al recibir ack: {e}")
            return

        # Bucle de peticiones
        while True:
            try:
                raw_pref = recv_all(s, PREFIX_LEN)
                print(f"[{SERVICE_NAME}] Prefijo entrante: {raw_pref!r}")
                length = int(raw_pref.decode())
                body = recv_all(s, length).decode()
                print(f"[{SERVICE_NAME}] Mensaje completo: {body}")

                sid = body[:len(SERVICE_NAME)]
                payload = body[len(SERVICE_NAME):]
                if sid == SERVICE_NAME:
                    # lógica de resta
                    if '-' in payload:
                        a, b = map(int, payload.split('-'))
                        result = str(a - b)
                    else:
                        result = f"ACK-{SERVICE_NAME}-{payload}-exitoso!"
                    resp_body = SERVICE_NAME + result
                    resp = str(len(resp_body)).zfill(PREFIX_LEN) + resp_body
                    print(f"[{SERVICE_NAME}] Enviando respuesta: {resp}")
                    s.sendall(resp.encode())
                else:
                    print(f"[{SERVICE_NAME}] Ignorado (destino {sid})")
            except ConnectionError:
                print(f"[{SERVICE_NAME}] Conexión cerrada por el bus")
                break
            except Exception as e:
                print(f"[{SERVICE_NAME}] Error inesperado: {e}")
                break

if __name__ == '__main__':
    main()
