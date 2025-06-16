from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Conversacion
from sqlalchemy.exc import IntegrityError

SERVICE_ID = "CVNEW"

def handle_cvnew(data: str) -> str:
    # data esperado: "usuario_a_id;usuario_b_id"
    parts = data.split(";")
    if len(parts) != 2:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        a_id, b_id = map(int, parts)
    except ValueError:
        return f"{SERVICE_ID}-ERR:id inválido"

    db = SessionLocal()
    try:
        # asegurar orden consistente (opcional)
        existing = (
            db.query(Conversacion)
              .filter_by(usuario_a_id=a_id, usuario_b_id=b_id)
              .first()
        )
        if not existing:
            conv = Conversacion(usuario_a_id=a_id, usuario_b_id=b_id)
            db.add(conv)
            db.commit()
            return f"{SERVICE_ID}-OK:{conv.conversacion_id}"
        return f"{SERVICE_ID}-OK:{existing.conversacion_id}"
    except IntegrityError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:conflicto conversación"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_cvnew)