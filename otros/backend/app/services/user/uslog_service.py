#!/usr/bin/env python3
# backend/app/services/user/uslog_service.py

from app.services.utils import serve
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

if __name__ == "__main__":
    serve(SERVICE_ID, handle_uslog)
