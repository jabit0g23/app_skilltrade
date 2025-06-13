from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo

SERVICE_ID = "AGRGT"

def handle_agrgt(data: str) -> str:
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
        return (
            f"{SERVICE_ID}-OK:" \
            f"{a.acuerdo_id};{a.proponente_usuario_id};{a.receptor_usuario_id};" \
            f"{a.estado_acuerdo.value}"
        )
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrgt)