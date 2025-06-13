from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Notificacion
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "NTFRD"

def handle_ntfrd(data: str) -> str:
    # data esperado: "notificacion_id"
    try:
        nid = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        n = db.query(Notificacion).get(nid)
        if not n:
            return f"{SERVICE_ID}-ERR:no encontrado"
        n.estado_leido = True
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_ntfrd)