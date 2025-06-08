### FILE: `test_cliente.py`

```
#!/usr/bin/env python3
import argparse
import socket
import sys


"""
python test_cliente.py USREG "alice;alice@ejemplo.com;secret123"

python test_cliente.py USLOG "alice@ejemplo.com;secret123"

python test_cliente.py USGET "2"

python test_cliente.py USUPD "2;AliceWonder;alice.wonder@ejemplo.com;newpass456"

python test_cliente.py USGET "2"
"""

HOST = "localhost"   # o "bus" si ejecutas dentro de otro contenedor
PORT = 5000
PREFIX_LEN = 5

def recv_all(sock, n):
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        buf += chunk
    return buf

def enviar_transaccion(service_id: str, payload: str):
    body = service_id + payload
    prefix = str(len(body)).zfill(PREFIX_LEN)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(f"> Conectado al bus {HOST}:{PORT}")
        msg = prefix + body
        print(f"> Enviando → {msg}")
        s.sendall(msg.encode())

        # recibimos el prefijo de la respuesta
        raw_pref = recv_all(s, PREFIX_LEN).decode()
        length = int(raw_pref)
        # ahora el cuerpo
        resp = recv_all(s, length).decode()
        print(f"< Recibido ← {resp}")
        return resp

def main():
    parser = argparse.ArgumentParser(
        description="Cliente de prueba para el bus SOA"
    )
    parser.add_argument("service", help="Código de servicio (p.ej. USREG, USLOG, PBNCR...)")
    parser.add_argument("data", help="Payload para el servicio (sin prefijo)")
    args = parser.parse_args()

    try:
        enviar_transaccion(args.service, args.data)
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

```

### FILE: `export_project.py`

```
#!/usr/bin/env python3
# export_project.py
# python -X utf8=1 ./export_project.py > proyecto.md

import os
import sys

def export_project(root_dir):
    """
    Recorre todo el directorio `root_dir` y genera un texto que incluye
    el path relativo y el contenido de cada archivo (en Markdown).
    """
    lines = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Omitir carpetas .git, node_modules, __pycache__
        dirnames[:] = [d for d in dirnames if d not in ('.git', 'node_modules', '__pycache__', 'venv', '.venv')]
        for fname in filenames:
            filepath = os.path.join(dirpath, fname)
            relpath = os.path.relpath(filepath, root_dir)
            lines.append(f"### FILE: `{relpath}`\n")
            try:
                # Solo leer archivos de texto
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except UnicodeDecodeError:
                content = "<Binario o codificación no UTF-8 omitido>"
            except Exception as e:
                content = f"<No se pudo leer: {e}>"
            lines.append("```")
            lines.append(content)
            lines.append("```\n")
    return "\n".join(lines)

if __name__ == "__main__":
    project_root = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.getcwd()
    export_text = export_project(project_root)
    # IMPRESIÓN FINAL
    print(export_text)

```

### FILE: `docker-compose.yml`

```
version: "3.8"

services:
  bus:
    image: jrgiadach/soabus:v1
    container_name: skilltrade_bus
    ports:
      - "5000:5000"
    restart: unless-stopped

  backend:
    build:
      context: ./backend
    container_name: skilltrade_backend
    volumes:
      - ./backend:/app
    working_dir: /app
    env_file:
      - ./backend/.env
    ports:
      - "8000:8000"
    depends_on:
      - bus
    command: uvicorn app.adapters.main:app --host 0.0.0.0 --port 8000 --reload
    restart: unless-stopped

  usreg:
    build:
      context: ./backend
    container_name: skilltrade_usreg
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.user.usreg_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  uslog:
    build:
      context: ./backend
    container_name: skilltrade_uslog
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.user.uslog_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  usget:
    build:
      context: ./backend
    container_name: skilltrade_usget
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.user.usget_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  usupd:
    build:
      context: ./backend
    container_name: skilltrade_usupd
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.user.usupd_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped


```

### FILE: `.gitignore`

```
*/venv
*.db
__pycache__
*.pyc
```

### FILE: `skilltrade.db`

```

```

### FILE: `README.md`

```
# app_skilltrade
```

### FILE: `proyecto.md`

```

```

### FILE: `backend/requirements.txt`

```
fastapi==0.95.1
uvicorn[standard]==0.22.0
SQLAlchemy==2.0.19
python-dotenv==1.0.0
alembic==1.11.1

```

### FILE: `backend/.env`

```
DATABASE_URL=sqlite:///./skilltrade.db

```

### FILE: `backend/skilltrade.db`

```
<Binario o codificación no UTF-8 omitido>
```

### FILE: `backend/Dockerfile`

```
FROM python:3.10-slim

# Instalar SQLite CLI (opcional, para debugging)
RUN apt-get update && \
    apt-get install -y sqlite3 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0"]

```

### FILE: `backend/proyecto.md`

```

```

### FILE: `backend/app/adapters/models.py`

```
# backend/app/models.py

import enum
from sqlalchemy import (
    Column, Integer, String, Text, Enum, ForeignKey,
    DECIMAL, TIMESTAMP, Boolean, Table, UniqueConstraint, Index
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base

# ——— Enums —————————————————————————————————————————————————————————————————————————

class TipoPublicacionEnum(enum.Enum):
    oferta = "oferta"
    demanda = "demanda"

class EstadoAcuerdoEnum(enum.Enum):
    propuesto = "propuesto"
    aceptado = "aceptado"
    rechazado = "rechazado"
    en_progreso = "en_progreso"
    finalizado_exitosamente = "finalizado_exitosamente"
    cancelado = "cancelado"

# ——— Tablas y modelos ——————————————————————————————————————————————————————————————————

class Usuario(Base):
    __tablename__ = "st_usuarios"

    usuario_id = Column(Integer, primary_key=True, index=True)
    nombre_usuario = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    contrasena = Column(String(255), nullable=False)
    reputacion_promedio = Column(DECIMAL(3,2), nullable=True)
    fecha_creacion = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, onupdate=func.now())

    publicaciones = relationship("Publicacion", back_populates="usuario")
    conversaciones_a = relationship("Conversacion",
                                    foreign_keys="[Conversacion.usuario_a_id]",
                                    back_populates="usuario_a")
    conversaciones_b = relationship("Conversacion",
                                    foreign_keys="[Conversacion.usuario_b_id]",
                                    back_populates="usuario_b")
    acuerdos_propuestos = relationship("Acuerdo",
                                       foreign_keys="[Acuerdo.proponente_usuario_id]",
                                       back_populates="proponente")
    acuerdos_recibidos = relationship("Acuerdo",
                                      foreign_keys="[Acuerdo.receptor_usuario_id]",
                                      back_populates="receptor")
    evaluaciones_emitidas = relationship("Evaluacion",
                                         foreign_keys="[Evaluacion.evaluador_usuario_id]",
                                         back_populates="evaluador")
    evaluaciones_recibidas = relationship("Evaluacion",
                                          foreign_keys="[Evaluacion.evaluado_usuario_id]",
                                          back_populates="evaluado")
    notificaciones = relationship("Notificacion", back_populates="usuario")

class Categoria(Base):
    __tablename__ = "st_categorias"

    categoria_id = Column(Integer, primary_key=True, index=True)
    nombre_categoria = Column(String(100), unique=True, nullable=False)

    publicaciones = relationship("Publicacion", back_populates="categoria")

class Etiqueta(Base):
    __tablename__ = "st_etiquetas"

    etiqueta_id = Column(Integer, primary_key=True, index=True)
    nombre_etiqueta = Column(String(50), unique=True, nullable=False)

# Tabla de asociación many-to-many
st_publicacion_etiquetas = Table(
    "st_publicacion_etiquetas", Base.metadata,
    Column("publicacion_id", Integer, ForeignKey("st_publicaciones.publicacion_id"), primary_key=True),
    Column("etiqueta_id",   Integer, ForeignKey("st_etiquetas.etiqueta_id"),      primary_key=True),
)

class Publicacion(Base):
    __tablename__ = "st_publicaciones"

    publicacion_id      = Column(Integer, primary_key=True, index=True)
    usuario_id          = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    tipo_publicacion    = Column(Enum(TipoPublicacionEnum), nullable=False)
    descripcion_habilidad = Column(Text, nullable=False)
    categoria_id        = Column(Integer, ForeignKey("st_categorias.categoria_id"), nullable=True)
    fecha_creacion      = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_actualizacion = Column(TIMESTAMP, onupdate=func.now())

    usuario    = relationship("Usuario", back_populates="publicaciones")
    categoria  = relationship("Categoria", back_populates="publicaciones")
    etiquetas  = relationship("Etiqueta", secondary=st_publicacion_etiquetas, backref="publicaciones")

class Conversacion(Base):
    __tablename__ = "st_conversaciones"

    conversacion_id = Column(Integer, primary_key=True, index=True)
    usuario_a_id    = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    usuario_b_id    = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    fecha_inicio    = Column(TIMESTAMP, nullable=False, server_default=func.now())

    usuario_a = relationship("Usuario", foreign_keys=[usuario_a_id], back_populates="conversaciones_a")
    usuario_b = relationship("Usuario", foreign_keys=[usuario_b_id], back_populates="conversaciones_b")
    mensajes  = relationship("Mensaje", back_populates="conversacion")

    __table_args__ = (
        UniqueConstraint("usuario_a_id", "usuario_b_id",
                         name="uq_conversacion_usuarios"),
    )

class Mensaje(Base):
    __tablename__ = "st_mensajes"

    mensaje_id         = Column(Integer, primary_key=True, index=True)
    conversacion_id    = Column(Integer, ForeignKey("st_conversaciones.conversacion_id"), nullable=False)
    remitente_usuario_id = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    contenido_mensaje  = Column(Text, nullable=False)
    fecha_envio        = Column(TIMESTAMP, nullable=False, server_default=func.now())
    leido              = Column(Boolean, nullable=False, server_default="0")

    conversacion = relationship("Conversacion", back_populates="mensajes")

    __table_args__ = (
        Index("ix_mensaje_conversacion_fecha", "conversacion_id", "fecha_envio"),
    )

class Acuerdo(Base):
    __tablename__ = "st_acuerdos"

    acuerdo_id                = Column(Integer, primary_key=True, index=True)
    proponente_usuario_id     = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    receptor_usuario_id       = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    publicacion_proponente_id = Column(Integer, ForeignKey("st_publicaciones.publicacion_id"), nullable=True)
    publicacion_receptor_id   = Column(Integer, ForeignKey("st_publicaciones.publicacion_id"), nullable=True)
    descripcion_propuesta_proponente = Column(Text, nullable=True)
    descripcion_propuesta_receptor   = Column(Text, nullable=True)
    estado_acuerdo            = Column(Enum(EstadoAcuerdoEnum), nullable=False)
    fecha_creacion_propuesta  = Column(TIMESTAMP, nullable=False, server_default=func.now())
    fecha_aceptacion          = Column(TIMESTAMP, nullable=True)
    fecha_finalizacion        = Column(TIMESTAMP, nullable=True)
    fecha_ultima_actualizacion= Column(TIMESTAMP, nullable=True)

    proponente = relationship("Usuario", foreign_keys=[proponente_usuario_id], back_populates="acuerdos_propuestos")
    receptor   = relationship("Usuario", foreign_keys=[receptor_usuario_id],   back_populates="acuerdos_recibidos")

class Evaluacion(Base):
    __tablename__ = "st_evaluaciones"

    evaluacion_id         = Column(Integer, primary_key=True, index=True)
    acuerdo_id            = Column(Integer, ForeignKey("st_acuerdos.acuerdo_id"), nullable=False)
    evaluador_usuario_id  = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    evaluado_usuario_id   = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    calificacion          = Column(Integer, nullable=False)
    comentario            = Column(Text, nullable=True)
    fecha_evaluacion      = Column(TIMESTAMP, nullable=False, server_default=func.now())

    evaluador = relationship("Usuario", foreign_keys=[evaluador_usuario_id], back_populates="evaluaciones_emitidas")
    evaluado  = relationship("Usuario", foreign_keys=[evaluado_usuario_id],  back_populates="evaluaciones_recibidas")

    __table_args__ = (
        Index("idx_evaluaciones_evaluado_fecha", "evaluado_usuario_id", "fecha_evaluacion"),
        Index("idx_evaluaciones_acuerdo", "acuerdo_id"),
    )

class Notificacion(Base):
    __tablename__ = "st_notificaciones"

    notificacion_id    = Column(Integer, primary_key=True, index=True)
    usuario_id         = Column(Integer, ForeignKey("st_usuarios.usuario_id"), nullable=False)
    mensaje_notificacion = Column(Text, nullable=False)
    estado_leido       = Column(Boolean, nullable=False, server_default="0")
    fecha_creacion     = Column(TIMESTAMP, nullable=False, server_default=func.now())

    usuario = relationship("Usuario", back_populates="notificaciones")

```

### FILE: `backend/app/adapters/main.py`

```
from fastapi import FastAPI
from .db import engine
from . import models

app = FastAPI()

# Esto ejecuta CREATE TABLE ... si no existe
models.Base.metadata.create_all(bind=engine)

# Aquí registras tus rutas REST y WebSockets

```

### FILE: `backend/app/adapters/db.py`

```
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./skilltrade.db")

# Para SQLite en multihilo es necesario este flag
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

```

### FILE: `backend/app/services/utils.py`

```
# backend/app/services/utils.py

import socket
from typing import Callable

HOST = "bus"      # nombre del contenedor bus en Docker Compose
PORT = 5000
PREFIX_LEN = 5

def create_bus_socket() -> socket.socket:
    """Conecta y devuelve un socket al bus."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def send_prefixed(sock: socket.socket, body: str):
    """Envía body con framing [5 dígitos de longitud] + body."""
    prefix = str(len(body)).zfill(PREFIX_LEN)
    sock.sendall((prefix + body).encode())

def recv_all(sock: socket.socket, n: int) -> bytes:
    """Recibe exactamente n bytes del socket."""
    buf = b""
    while len(buf) < n:
        chunk = sock.recv(n - len(buf))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        buf += chunk
    return buf

def recv_message(sock: socket.socket) -> str:
    """Recibe un mensaje entero (prefijo + payload) y devuelve solo el payload."""
    raw_pref = recv_all(sock, PREFIX_LEN).decode()
    length = int(raw_pref)
    return recv_all(sock, length).decode()

def serve(service_id: str, handler: Callable[[str], str]):
    """
    Loop genérico de un microservicio:
    1) Anuncia con sinit<service_id>
    2) Espera ack
    3) Repeatedly recibe mensajes, filtra por service_id y delega a handler
    4) Envía la respuesta que devuelve handler
    """
    sock = create_bus_socket()
    send_prefixed(sock, f"sinit{service_id}")
    _ = recv_message(sock)  # ack del bus

    while True:
        msg = recv_message(sock)
        cmd, payload = msg[:len(service_id)], msg[len(service_id):]
        if cmd != service_id:
            continue
        response = handler(payload)
        send_prefixed(sock, response)

```

### FILE: `backend/app/services/user/uslog_service.py`

```
#!/usr/bin/env python3
# backend/app/services/user/uslog_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
import hashlib

SERVICE_ID = "USLOG"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_uslog(data: str) -> str:
    # data esperado: "email;contrasena"
    try:
        email, pwd = data.split(";")
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    user = db.query(Usuario).filter_by(email=email).first()
    db.close()
    if not user or user.contrasena != hash_pwd(pwd):
        return f"{SERVICE_ID}-ERR:credenciales inválidas"
    return f"{SERVICE_ID}-OK:{user.usuario_id};{user.nombre_usuario}"

if __name__ == "__main__":
    serve(SERVICE_ID, handle_uslog)

```

### FILE: `backend/app/services/user/usupd_service.py`

```
#!/usr/bin/env python3
# backend/app/services/user/usupd_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib

SERVICE_ID = "USUPD"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_usupd(data: str) -> str:
    # data esperado: "usuario_id;nombre;email;contrasena"
    parts = data.split(";")
    if len(parts) != 4:
        return f"{SERVICE_ID}-ERR:formato inválido"

    try:
        user_id = int(parts[0])
    except ValueError:
        return f"{SERVICE_ID}-ERR:id inválido"

    nombre, email, pwd = parts[1], parts[2], parts[3]

    db = SessionLocal()
    user = db.query(Usuario).get(user_id)
    if not user:
        db.close()
        return f"{SERVICE_ID}-ERR:usuario no encontrado"

    user.nombre_usuario = nombre
    user.email = email
    user.contrasena = hash_pwd(pwd)

    try:
        db.commit()
        return f"{SERVICE_ID}-OK"
    except IntegrityError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:email ya existente"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usupd)

```

### FILE: `backend/app/services/user/usreg_service.py`

```
#!/usr/bin/env python3
# backend/app/services/user/usreg_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario
from sqlalchemy.exc import IntegrityError
import hashlib

SERVICE_ID = "USREG"

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def handle_usreg(data: str) -> str:
    # data esperado: "nombre;email;contrasena"
    try:
        nombre, email, pwd = data.split(";")
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    user = Usuario(
        nombre_usuario=nombre,
        email=email,
        contrasena=hash_pwd(pwd)
    )
    try:
        db.add(user)
        db.commit()
        return f"{SERVICE_ID}-OK:{user.usuario_id}"
    except IntegrityError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:Email existente"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usreg)

```

### FILE: `backend/app/services/user/usget_service.py`

```
#!/usr/bin/env python3
# backend/app/services/user/usget_service.py

from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Usuario

SERVICE_ID = "USGET"

def handle_usget(data: str) -> str:
    # data esperado: "usuario_id"
    try:
        user_id = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    user = db.query(Usuario).get(user_id)
    db.close()
    if not user:
        return f"{SERVICE_ID}-ERR:usuario no encontrado"

    rep = user.reputacion_promedio or 0
    return (
        f"{SERVICE_ID}-OK:"
        f"{user.usuario_id};"
        f"{user.nombre_usuario};"
        f"{user.email};"
        f"{rep}"
    )

if __name__ == "__main__":
    serve(SERVICE_ID, handle_usget)

```

### FILE: `otros/estructura.txt`

```
Como referencia de la arquitectura.

skilltrade/
├── README.md
├── LICENSE
├── .gitignore
├── docker-compose.yml
├── .env.example
│
├── backend/                   # API y microservicios Python
│   ├── Dockerfile            # Para construir la imagen del backend
│   ├── requirements.txt      # Dependencias de Python
│   ├── alembic.ini           # Configuración de migraciones (Alembic)
│   ├── migrations/           # Scripts de migración de BD
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI entrypoint (incluye WS adapter)
│   │   ├── config.py         # Carga .env, settings
│   │   ├── models.py         # SQLAlchemy/Tortoise models
│   │   ├── db.py             # Inicialización de SQLite + sesión
│   │   ├── services/         # Lógica de cada microservicio (User, Pub, Chat…)
│   │   ├── adapters/         # Código de traducción WS ↔ raw-TCP
│   │   └── tests/            # Tests unitarios / de integración
│
├── frontend/                  # App web React
│   ├── Dockerfile            # Imagen ligera de producción
│   ├── package.json
│   ├── vite.config.ts        # (o CRA config)
│   ├── public/               # index.html, favicon, assets estáticos
│   ├── src/
│   │   ├── main.jsx          # Punto de entrada (ReactDOM.render)
│   │   ├── App.jsx
│   │   ├── components/       # UI components (cards, modals, etc.)
│   │   ├── pages/            # Vistas (Home, Perfil, Chat…)
│   │   ├── hooks/            # e.g. useAuth, useWebSocket
│   │   ├── services/         # API clients (WebSocket wrapper)
│   │   ├── store/            # (opcional) Redux / Zustand / Context
│   │   └── assets/           # Imágenes, estilos globales, fuentes
│
└── docs/                      # Diseño, wireframes, especificaciones
    ├── architecture.md
    └── api-contract.md

```

### FILE: `otros/suma_servi.py`

```
# servicio_sumar.py
import socket

HOST = 'localhost'
BUS_PORT = 5000
PREFIX_LEN = 5
SERVICE_NAME = 'sumar'

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        data += chunk
    return data

def main():
    with socket.socket() as s:
        print(f"[{SERVICE_NAME}] Conectando al bus {HOST}:{BUS_PORT}…")
        s.connect((HOST, BUS_PORT))
        print(f"[{SERVICE_NAME}] Conexión establecida")

        # Anuncio
        init = 'sinit' + SERVICE_NAME
        packet = str(len(init)).zfill(PREFIX_LEN) + init
        print(f"[{SERVICE_NAME}] Enviando anuncio: {packet}")
        s.sendall(packet.encode())

        # Recibo ack
        try:
            raw_pref = recv_all(s, PREFIX_LEN)
            ack_len = int(raw_pref.decode())
            ack_body = recv_all(s, ack_len).decode()
            print(f"[{SERVICE_NAME}] Ack recibido: {ack_body}")
        except Exception as e:
            print(f"[{SERVICE_NAME}] Error al recibir ack: {e}")
            return

        # Bucle de peticiones
        while True:
            try:
                raw_pref = recv_all(s, PREFIX_LEN)
                print(f"[{SERVICE_NAME}] Prefijo entrante: {raw_pref!r}")
                length = int(raw_pref.decode())
                body = recv_all(s, length).decode()
                print(f"[{SERVICE_NAME}] Mensaje completo: {body}")

                sid = body[:len(SERVICE_NAME)]
                payload = body[len(SERVICE_NAME):]
                if sid == SERVICE_NAME:
                    # lógica de suma
                    if '-' in payload:
                        a, b = map(int, payload.split('-'))
                        result = str(a + b)
                    else:
                        result = f"ACK-{SERVICE_NAME}-{payload}-exitoso!"
                    resp_body = SERVICE_NAME + result
                    resp = str(len(resp_body)).zfill(PREFIX_LEN) + resp_body
                    print(f"[{SERVICE_NAME}] Enviando respuesta: {resp}")
                    s.sendall(resp.encode())
                else:
                    print(f"[{SERVICE_NAME}] Ignorado (destino {sid})")
            except ConnectionError:
                print(f"[{SERVICE_NAME}] Conexión cerrada por el bus")
                break
            except Exception as e:
                print(f"[{SERVICE_NAME}] Error inesperado: {e}")
                break

if __name__ == '__main__':
    main()

```

### FILE: `otros/cliente.py`

```
# cliente.py
import socket

HOST = 'localhost'
BUS_PORT = 5000
PREFIX_LEN = 5

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        data += chunk
    return data

def enviar_transaccion(service_id, payload):
    with socket.socket() as s:
        print(f"[CLIENT] Conectando al bus {HOST}:{BUS_PORT}…")
        s.connect((HOST, BUS_PORT))
        print(f"[CLIENT] Conexión establecida")

        body = service_id + payload
        msg = str(len(body)).zfill(PREFIX_LEN) + body
        print(f"[CLIENT] Enviando: {msg}")
        s.sendall(msg.encode())

        raw_pref = recv_all(s, PREFIX_LEN)
        length = int(raw_pref.decode())
        resp_body = recv_all(s, length).decode()
        print(f"[CLIENT] Respuesta recibida: {resp_body}")

if __name__ == '__main__':
    enviar_transaccion('sumar', '10-3')
    enviar_transaccion('resta', '10-3')

```

### FILE: `otros/resta_servi.py`

```
# servicio_resta.py
import socket

HOST = 'localhost'
BUS_PORT = 5000
PREFIX_LEN = 5
SERVICE_NAME = 'resta'

def recv_all(sock, n):
    data = b''
    while len(data) < n:
        chunk = sock.recv(n - len(data))
        if not chunk:
            raise ConnectionError("Socket cerrado por el bus")
        data += chunk
    return data

def main():
    with socket.socket() as s:
        print(f"[{SERVICE_NAME}] Conectando al bus {HOST}:{BUS_PORT}…")
        s.connect((HOST, BUS_PORT))
        print(f"[{SERVICE_NAME}] Conexión establecida")

        # Anuncio
        init = 'sinit' + SERVICE_NAME
        packet = str(len(init)).zfill(PREFIX_LEN) + init
        print(f"[{SERVICE_NAME}] Enviando anuncio: {packet}")
        s.sendall(packet.encode())

        # Recibo ack
        try:
            raw_pref = recv_all(s, PREFIX_LEN)
            ack_len = int(raw_pref.decode())
            ack_body = recv_all(s, ack_len).decode()
            print(f"[{SERVICE_NAME}] Ack recibido: {ack_body}")
        except Exception as e:
            print(f"[{SERVICE_NAME}] Error al recibir ack: {e}")
            return

        # Bucle de peticiones
        while True:
            try:
                raw_pref = recv_all(s, PREFIX_LEN)
                print(f"[{SERVICE_NAME}] Prefijo entrante: {raw_pref!r}")
                length = int(raw_pref.decode())
                body = recv_all(s, length).decode()
                print(f"[{SERVICE_NAME}] Mensaje completo: {body}")

                sid = body[:len(SERVICE_NAME)]
                payload = body[len(SERVICE_NAME):]
                if sid == SERVICE_NAME:
                    # lógica de resta
                    if '-' in payload:
                        a, b = map(int, payload.split('-'))
                        result = str(a - b)
                    else:
                        result = f"ACK-{SERVICE_NAME}-{payload}-exitoso!"
                    resp_body = SERVICE_NAME + result
                    resp = str(len(resp_body)).zfill(PREFIX_LEN) + resp_body
                    print(f"[{SERVICE_NAME}] Enviando respuesta: {resp}")
                    s.sendall(resp.encode())
                else:
                    print(f"[{SERVICE_NAME}] Ignorado (destino {sid})")
            except ConnectionError:
                print(f"[{SERVICE_NAME}] Conexión cerrada por el bus")
                break
            except Exception as e:
                print(f"[{SERVICE_NAME}] Error inesperado: {e}")
                break

if __name__ == '__main__':
    main()

```

