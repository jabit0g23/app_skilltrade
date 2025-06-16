#!/usr/bin/env python3
# backend/app/services/user/usreg_service.py

from app.services.utils import serve
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
        return f"{SERVICE_ID}-ERR:formato inválido"

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

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usreg)
