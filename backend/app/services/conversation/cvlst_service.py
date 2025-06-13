from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Conversacion

SERVICE_ID = "CVLST"

def handle_cvlst(data: str) -> str:
    # data esperado: "usuario_id"
    try:
        u_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        convs = (
            db.query(Conversacion)
              .filter(
                  (Conversacion.usuario_a_id == u_id) |
                  (Conversacion.usuario_b_id == u_id)
              )
              .all()
        )
        if not convs:
            return f"{SERVICE_ID}-OK:"
        lines = [f"{c.conversacion_id};{c.usuario_a_id};{c.usuario_b_id}" for c in convs]
        return f"{SERVICE_ID}-OK:" + "|".join(lines)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_cvlst)