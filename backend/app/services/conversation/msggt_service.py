from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Mensaje
from sqlalchemy.orm import joinedload

SERVICE_ID = "MSGGT"

def handle_msggt(data: str) -> str:
    # data esperado: "conversacion_id"
    try:
        conv_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        msgs = (
            db.query(Mensaje)
              .options(joinedload(Mensaje.conversacion))
              .filter_by(conversacion_id=conv_id)
              .order_by(Mensaje.fecha_envio)
              .all()
        )
        if not msgs:
            return f"{SERVICE_ID}-OK:"
        lines = [f"{m.mensaje_id};{m.remitente_usuario_id};{m.contenido_mensaje};{int(m.leido)}" for m in msgs]
        return f"{SERVICE_ID}-OK:" + "|".join(lines)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_msggt)