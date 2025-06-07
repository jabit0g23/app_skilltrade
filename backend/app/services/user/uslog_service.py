#!/usr/bin/env python3
# backend/app/services/user/uslog_service.py

from app.services.utils import create_bus_socket, send_prefixed, recv_message
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
import hashlib

SERVICE_ID = "USLOG"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_uslog(data: str) -> str:
    # data esperado: "email;contrasena"
    try:
        email, pwd = data.split(";")
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"
    db = SessionLocal()
    user = db.query(Usuario).filter_by(email=email).first()
    db.close()
    if not user or user.contrasena != hash_pwd(pwd):
        return f"{SERVICE_ID}-ERR:credenciales inválidas"
    return f"{SERVICE_ID}-OK:{user.usuario_id};{user.nombre_usuario}"

def main():
    sock = create_bus_socket()
    send_prefixed(sock, f"sinit{SERVICE_ID}")
    _ = recv_message(sock)

    while True:
        msg = recv_message(sock)
        cmd, payload = msg[:len(SERVICE_ID)], msg[len(SERVICE_ID):]
        if cmd != SERVICE_ID:
            continue
        response = handle_uslog(payload)
        send_prefixed(sock, response)

if __name__ == "__main__":
    main()
