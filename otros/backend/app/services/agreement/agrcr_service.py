from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRCR"

def handle_agrcr(data: str) -> str:
    # data esperado: "proponente_id;receptor_id;pub_prop_id;pub_rec_id;descripcion"
    parts = data.split(";", 4)
    if len(parts) != 5:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        prop_id = int(parts[0])
        rec_id = int(parts[1])
        pub_prop = int(parts[2])
        pub_rec = int(parts[3])
        desc = parts[4]
    except ValueError:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    db = SessionLocal()
    try:
        agr = Acuerdo(
            proponente_usuario_id=prop_id,
            receptor_usuario_id=rec_id,
            publicacion_proponente_id=pub_prop,
            publicacion_receptor_id=pub_rec,
            descripcion_propuesta_proponente=desc,
            estado_acuerdo=EstadoAcuerdoEnum.propuesto
        )
        db.add(agr)
        db.commit()
        return f"{SERVICE_ID}-OK:{agr.acuerdo_id}"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:inserción fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrcr)