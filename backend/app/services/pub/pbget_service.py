#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion

SERVICE_ID = "PBGET"

def handle_pbget(data: str) -> str:
    # data esperado: "publicacion_id"
    try:
        pid = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        p = db.query(Publicacion).get(pid)
        if not p:
            return f"{SERVICE_ID}-ERR:no encontrado"
        cat = p.categoria.nombre_categoria if p.categoria else ""
        tags = ",".join(t.nombre_etiqueta for t in p.etiquetas)
        return (f"{SERVICE_ID}-OK:"
                f"{p.publicacion_id};{p.usuario_id};{p.tipo_publicacion.value};"
                f"{p.descripcion_habilidad};{cat};{tags}")
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbget)
