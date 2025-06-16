from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from .db import engine
from . import models
import socket

from app.services.utils import PREFIX_LEN, create_bus_socket, send_prefixed, recv_all

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            msg = await ws.receive_text()
            body = msg[PREFIX_LEN:]
            bus = create_bus_socket()
            send_prefixed(bus, body)
            
             # 1) Leer el prefijo que envía el bus (5 bytes)
            raw_pref = recv_all(bus, PREFIX_LEN).decode()
            # 2) Parsear la longitud y leer ese número de bytes
            length = int(raw_pref)
            payload = recv_all(bus, length).decode()
            bus.close()
            # 3) Reenviar al cliente el prefijo + payload EXACTO
            await ws.send_text(raw_pref + payload)
    except WebSocketDisconnect:
        pass

