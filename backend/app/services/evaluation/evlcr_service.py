from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Evaluacion, Acuerdo
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "EVLCR"

def handle_evlcr(data: str) -> str:
    # data esperado: "acuerdo_id;evaluador_id;evaluado_id;calificacion;comentario"
    parts = data.split(";", 4)
    if len(parts) != 5:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        aid = int(parts[0])
        evl = int(parts[1])
        evd = int(parts[2])
        cal = int(parts[3])
        com = parts[4]
    except ValueError:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    db = SessionLocal()
    try:
        # verificar acuerdo finalizado
        agr = db.query(Acuerdo).get(aid)
        if not agr or agr.estado_acuerdo != agr.estado_acuerdo.finalizado_exitosamente:
            return f"{SERVICE_ID}-ERR:acuerdo no finalizado"
        eval_obj = Evaluacion(
            acuerdo_id=aid,
            evaluador_usuario_id=evl,
            evaluado_usuario_id=evd,
            calificacion=cal,
            comentario=com
        )
        db.add(eval_obj)
        db.commit()
        return f"{SERVICE_ID}-OK:{eval_obj.evaluacion_id}"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:inserción fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_evlcr)