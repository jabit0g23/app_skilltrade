from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Evaluacion

SERVICE_ID = "EVLGT"

def handle_evlgt(data: str) -> str:
    # data esperado: "usuario_id"
    try:
        u_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        evals = db.query(Evaluacion).filter_by(evaluado_usuario_id=u_id).all()
        if not evals:
            return f"{SERVICE_ID}-OK:"
        lines = [f"{e.evaluacion_id};{e.acuerdo_id};{e.evaluador_usuario_id};{e.calificacion};{e.comentario}" for e in evals]
        return f"{SERVICE_ID}-OK:" + "|".join(lines)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_evlgt)