#!/usr/bin/env python3
# backend/app/services/user/usget_service.py

from app.services.utils import create_bus_socket, send_prefixed, recv_message
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
import hashlib

SERVICE_ID = "USGET"

def handle_usget(data: str) -> str:
    """
    data esperado: "usuario_id"
    Devuelve SERVICE_ID-OK:<id>;<nombre>;<email>;<reputacion_promedio>
    o SERVICE_ID-ERR:...
    """
    try:
        user_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    user = db.query(Usuario).get(user_id)
    db.close()

    if not user:
        return f"{SERVICE_ID}-ERR:usuario no encontrado"

    # reputacion_promedio puede ser None
    rep = user.reputacion_promedio or 0
    return (
        f"{SERVICE_ID}-OK:"
        f"{user.usuario_id};"
        f"{user.nombre_usuario};"
        f"{user.email};"
        f"{rep}"
    )

def main():
    sock = create_bus_socket()
    send_prefixed(sock, f"sinit{SERVICE_ID}")
    _ = recv_message(sock)

    while True:
        msg = recv_message(sock)
        cmd, payload = msg[:len(SERVICE_ID)], msg[len(SERVICE_ID):]
        if cmd != SERVICE_ID:
            continue
        resp = handle_usget(payload)
        send_prefixed(sock, resp)

if __name__ == "__main__":
    main()
