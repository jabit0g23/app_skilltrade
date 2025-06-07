#!/usr/bin/env python3
# backend/app/services/user/usreg_service.py

from app.services.utils import create_bus_socket, send_prefixed, recv_message
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib

SERVICE_ID = "USREG"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_usreg(data: str) -> str:
    # data esperado: "nombre;email;contrasena"
    try:
        nombre, email, pwd = data.split(";")
    except ValueError:
        return "Error: formato inválido"
    db = SessionLocal()
    user = Usuario(
        nombre_usuario=nombre,
        email=email,
        contrasena=hash_pwd(pwd)
    )
    try:
        db.add(user)
        db.commit()
        return f"{SERVICE_ID}-OK:{user.usuario_id}"
    except IntegrityError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:Email existente"
    finally:
        db.close()

def main():
    sock = create_bus_socket()

    # 1) Anunciar al bus
    send_prefixed(sock, f"sinit{SERVICE_ID}")

    # 2) Esperar ACK de bus (opcional)
    _ = recv_message(sock)

    # 3) Bucle de peticiones
    while True:
        msg = recv_message(sock)       # e.g. "USREGjuan;juan@x.com;1234"
        cmd, payload = msg[:len(SERVICE_ID)], msg[len(SERVICE_ID):]
        if cmd != SERVICE_ID:
            continue
        result = handle_usreg(payload)  # lógicamente incluye SERVICE_ID-OK o -ERR
        send_prefixed(sock, result)

if __name__ == "__main__":
    main()
