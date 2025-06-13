#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion, Categoria, Etiqueta, TipoPublicacionEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "PBNCR"

def handle_pbncr(data: str) -> str:
    # data esperado: "usuario_id;tipo;descripcion;categoria_id;et1,et2"
    parts = data.split(";")
    if len(parts) != 5:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        user_id = int(parts[0])
        tipo = TipoPublicacionEnum(parts[1])
        descripcion = parts[2]
        cat_id = int(parts[3])
    except Exception:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    etiquetas = [e.strip() for e in parts[4].split(",") if e.strip()]
    db = SessionLocal()
    try:
        # validar categoría si viene
        if cat_id:
            cat = db.query(Categoria).get(cat_id)
            if not cat:
                return f"{SERVICE_ID}-ERR:categoria no encontrada"
        pub = Publicacion(
            usuario_id=user_id,
            tipo_publicacion=tipo,
            descripcion_habilidad=descripcion,
            categoria_id=cat_id or None
        )
        # administrar etiquetas
        for nombre in etiquetas:
            tag = db.query(Etiqueta).filter_by(nombre_etiqueta=nombre).first()
            if not tag:
                tag = Etiqueta(nombre_etiqueta=nombre)
            pub.etiquetas.append(tag)

        db.add(pub)
        db.commit()
        return f"{SERVICE_ID}-OK:{pub.publicacion_id}"
    except SQLAlchemyError as e:
        db.rollback()
        return f"{SERVICE_ID}-ERR:{e.__class__.__name__}"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbncr)
