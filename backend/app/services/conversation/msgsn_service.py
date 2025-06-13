from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Mensaje
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "MSGSN"

def handle_msgsn(data: str) -> str:
    # data esperado: "conversacion_id;remitente_id;contenido"
    parts = data.split(";", 2)
    if len(parts) != 3:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        conv_id = int(parts[0])
        remit_id = int(parts[1])
        content = parts[2]
    except ValueError:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    db = SessionLocal()
    try:
        msg = Mensaje(
            conversacion_id=conv_id,
            remitente_usuario_id=remit_id,
            contenido_mensaje=content,
            leido=False
        )
        db.add(msg)
        db.commit()
        return f"{SERVICE_ID}-OK:{msg.mensaje_id}"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:inserción fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_msgsn)