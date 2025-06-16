#!/usr/bin/env python3
# backend/app/services/user/usget_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario

SERVICE_ID = "USGET"

def handle_usget(data: str) -> str:
    # data esperado: "usuario_id"
    try:
        user_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    user = db.query(Usuario).get(user_id)
    db.close()
    if not user:
        return f"{SERVICE_ID}-ERR:usuario no encontrado"

    rep = user.reputacion_promedio or 0
    return (
        f"{SERVICE_ID}-OK:"
        f"{user.usuario_id};"
        f"{user.nombre_usuario};"
        f"{user.email};"
        f"{rep}"
    )

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usget)
