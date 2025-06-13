from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Notificacion

SERVICE_ID = "NTFGT"

def handle_ntfgt(data: str) -> str:
    # data esperado: "usuario_id"
    try:
        u_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        notifs = db.query(Notificacion).filter_by(usuario_id=u_id).all()
        if not notifs:
            return f"{SERVICE_ID}-OK:"
        lines = [f"{n.notificacion_id};{int(n.estado_leido)};{n.mensaje_notificacion}" for n in notifs]
        return f"{SERVICE_ID}-OK:" + "|".join(lines)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_ntfgt)