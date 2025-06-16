#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion

SERVICE_ID = "PBDEL"

def handle_pbdel(data: str) -> str:
    # data esperado: "usuario_id;publicacion_id"
    parts = data.split(";")
    if len(parts) != 2:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        user_id = int(parts[0])
        pub_id = int(parts[1])
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        p = db.query(Publicacion).get(pub_id)
        if not p:
            return f"{SERVICE_ID}-ERR:no encontrado"
        if p.usuario_id != user_id:
            return f"{SERVICE_ID}-ERR:prohibido"
        db.delete(p)
        db.commit()
        return f"{SERVICE_ID}-OK"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbdel)
