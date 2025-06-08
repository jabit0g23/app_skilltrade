#!/usr/bin/env python3
# backend/app/services/user/usupd_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib

SERVICE_ID = "USUPD"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_usupd(data: str) -> str:
    # data esperado: "usuario_id;nombre;email;contrasena"
    parts = data.split(";")
    if len(parts) != 4:
        return f"{SERVICE_ID}-ERR:formato inválido"

    try:
        user_id = int(parts[0])
    except ValueError:
        return f"{SERVICE_ID}-ERR:id inválido"

    nombre, email, pwd = parts[1], parts[2], parts[3]

    db = SessionLocal()
    user = db.query(Usuario).get(user_id)
    if not user:
        db.close()
        return f"{SERVICE_ID}-ERR:usuario no encontrado"

    user.nombre_usuario = nombre
    user.email = email
    user.contrasena = hash_pwd(pwd)

    try:
        db.commit()
        return f"{SERVICE_ID}-OK"
    except IntegrityError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:email ya existente"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usupd)
