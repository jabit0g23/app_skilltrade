from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRAC"

def handle_agrac(data: str) -> str:
    # data esperado: "acuerdo_id"
    try:
        aid = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        a = db.query(Acuerdo).get(aid)
        if not a:
            return f"{SERVICE_ID}-ERR:no encontrado"
        if a.estado_acuerdo != EstadoAcuerdoEnum.propuesto:
            return f"{SERVICE_ID}-ERR:estado inválido"
        a.estado_acuerdo = EstadoAcuerdoEnum.aceptado
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrac)