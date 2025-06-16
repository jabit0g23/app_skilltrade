#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion, Categoria, TipoPublicacionEnum
from sqlalchemy.orm import joinedload

SERVICE_ID = "PBLST"

def handle_pblst(data: str) -> str:
    # data esperado: "tipo;texto_busqueda"
    parts = data.split(";")
    if len(parts) != 2:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        tipo = TipoPublicacionEnum(parts[0])
        texto = parts[1]
    except Exception:
        return f"{SERVICE_ID}-ERR:tipo inválido"

    db = SessionLocal()
    try:
        pubs = (
            db.query(Publicacion)
              .options(joinedload(Publicacion.categoria), joinedload(Publicacion.etiquetas))
              .filter(
                  Publicacion.tipo_publicacion == tipo,
                  Publicacion.descripcion_habilidad.ilike(f"%{texto}%")
              )
              .all()
        )
        if not pubs:
            return f"{SERVICE_ID}-OK:"

        líneas = []
        for p in pubs:
            cat = p.categoria.nombre_categoria if p.categoria else ""
            tags = ",".join(t.nombre_etiqueta for t in p.etiquetas)
            # recortamos descripción para no saturar
            desc = p.descripcion_habilidad
            líneas.append(f"{p.publicacion_id};{p.usuario_id};{p.tipo_publicacion.value};"
                          f"{desc[:30]}…;{cat};{tags}")
        return f"{SERVICE_ID}-OK:" + "|".join(líneas)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pblst)
