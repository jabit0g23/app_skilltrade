### FILE: `test_cliente.py`

```
#!/usr/bin/env python3
import argparse
import socket
import sys


"""
Testear el servicio de usuario:

python test_cliente.py USREG "alice;alice@ejemplo.com;secret123"
python test_cliente.py USLOG "alice@ejemplo.com;secret123"
python test_cliente.py USGET "2"
python test_cliente.py USUPD "2;AliceWonder;alice.wonder@ejemplo.com;newpass456"
python test_cliente.py USGET "2"


Testear el servicio de publicaciones:

python test_cliente.py PBNCR "1;oferta;Desarrollo de API en Python;2;dev,backend"
python test_cliente.py PBLST "oferta;API"
python test_cliente.py PBGET "5"
python test_cliente.py PBDEL "1;5"
python test_cliente.py PBGET "5"

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

  pbncr:
    build:
      context: ./backend
    container_name: skilltrade_pbncr
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.publication.pbncr_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  pblst:
    build:
      context: ./backend
    container_name: skilltrade_pblst
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.publication.pblst_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  pbget:
    build:
      context: ./backend
    container_name: skilltrade_pbget
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.publication.pbget_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  pbdel:
    build:
      context: ./backend
    container_name: skilltrade_pbdel
    working_dir: /app
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.publication.pbdel_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  cvnew:
    build:
      context: ./backend
    container_name: skilltrade_cvnew
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.conversation.cvnew_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  cvlst:
    build:
      context: ./backend
    container_name: skilltrade_cvlst
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.conversation.cvlst_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  msggt:
    build:
      context: ./backend
    container_name: skilltrade_msggt
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.conversation.msggt_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  msgsn:
    build:
      context: ./backend
    container_name: skilltrade_msgsn
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.conversation.msgsn_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  agrcr:
    build:
      context: ./backend
    container_name: skilltrade_agrcr
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.agreement.agrcr_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  agrgt:
    build:
      context: ./backend
    container_name: skilltrade_agrgt
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.agreement.agrgt_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  agrac:
    build:
      context: ./backend
    container_name: skilltrade_agrac
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.agreement.agrac_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  agrrj:
    build:
      context: ./backend
    container_name: skilltrade_agrrj
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.agreement.agrrj_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  agrfn:
    build:
      context: ./backend
    container_name: skilltrade_agrfn
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.agreement.agrfn_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  evlcr:
    build:
      context: ./backend
    container_name: skilltrade_evlcr
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.evaluation.evlcr_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  evlgt:
    build:
      context: ./backend
    container_name: skilltrade_evlgt
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.evaluation.evlgt_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  ntfgt:
    build:
      context: ./backend
    container_name: skilltrade_ntfgt
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.notification.ntfgt_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped

  ntfrd:
    build:
      context: ./backend
    container_name: skilltrade_ntfrd
    volumes:
      - ./backend:/app
    depends_on:
      - bus
    command: ["python","-m","app.services.notification.ntfrd_service"]
    environment:
      - PYTHONPATH=/app
    restart: unless-stopped


```

### FILE: `comandos.txt`

```
conectarse a la bbdd:

cd backend
sqlite3 skilltrade.db
sqlite> .tables
SELECT count(*) FROM st_usuarios;
```

### FILE: `.gitignore`

```
*/venv
*.db
__pycache__
*.pyc



# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
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

### FILE: `backend/seed_db.py`

```
#!/usr/bin/env python3
# seed_db.py

from app.adapters.db import SessionLocal, engine, Base
from app.adapters.models import (
    Usuario, Categoria, Etiqueta, Publicacion,
    Conversacion, Mensaje, Acuerdo, Evaluacion, Notificacion
)
import hashlib

def hash_pwd(pwd: str) -> str:
    return hashlib.sha256(pwd.encode()).hexdigest()

def seed():
    # Asegura que las tablas existen
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Usuarios
        u1 = Usuario(
            usuario_id=1,
            nombre_usuario='alice',
            email='alice@example.com',
            contrasena=hash_pwd('alice123'),
            reputacion_promedio=4.5
        )
        u2 = Usuario(
            usuario_id=2,
            nombre_usuario='bob',
            email='bob@example.com',
            contrasena=hash_pwd('bob123'),
            reputacion_promedio=3.8
        )
        db.add_all([u1, u2])

        # 2. Categorías
        c1 = Categoria(categoria_id=1, nombre_categoria='Desarrollo')
        c2 = Categoria(categoria_id=2, nombre_categoria='Diseño')
        db.add_all([c1, c2])

        # 3. Etiquetas
        t1 = Etiqueta(etiqueta_id=1, nombre_etiqueta='python')
        t2 = Etiqueta(etiqueta_id=2, nombre_etiqueta='backend')
        t3 = Etiqueta(etiqueta_id=3, nombre_etiqueta='frontend')
        db.add_all([t1, t2, t3])

        db.flush()  # fuerza asignación de IDs

        # 4. Publicaciones
        p1 = Publicacion(
            publicacion_id=1,
            usuario_id=1,
            tipo_publicacion='oferta',
            descripcion_habilidad='Desarrollo de API REST con FastAPI',
            categoria_id=1,
            etiquetas=[t1, t2]
        )
        p2 = Publicacion(
            publicacion_id=2,
            usuario_id=2,
            tipo_publicacion='demanda',
            descripcion_habilidad='Necesita diseño de interfaz en React',
            categoria_id=2,
            etiquetas=[t3]
        )
        db.add_all([p1, p2])

        # 5. Conversación y mensajes
        conv = Conversacion(conversacion_id=1, usuario_a_id=1, usuario_b_id=2)
        m1 = Mensaje(mensaje_id=1, conversacion_id=1, remitente_usuario_id=1,
                     contenido_mensaje='Hola Bob, vi tu publicación y me interesa tu servicio de diseño.', leido=True)
        m2 = Mensaje(mensaje_id=2, conversacion_id=1, remitente_usuario_id=2,
                     contenido_mensaje='Hola Alice, con gusto trabajo en el diseño, ¿podemos coordinar?', leido=False)
        db.add_all([conv, m1, m2])

        # 6. Acuerdo
        a = Acuerdo(
            acuerdo_id=1,
            proponente_usuario_id=1,
            receptor_usuario_id=2,
            publicacion_proponente_id=1,
            publicacion_receptor_id=2,
            descripcion_propuesta_proponente='Te ofrezco el API a cambio del diseño',
            estado_acuerdo='propuesto'
        )
        db.add(a)

        # 7. Evaluación
        e = Evaluacion(
            evaluacion_id=1,
            acuerdo_id=1,
            evaluador_usuario_id=1,
            evaluado_usuario_id=2,
            calificacion=5,
            comentario='Excelente trabajo'
        )
        db.add(e)

        # 8. Notificación
        n = Notificacion(
            notificacion_id=1,
            usuario_id=2,
            mensaje_notificacion='Has recibido una nueva propuesta de trueque',
            estado_leido=False
        )
        db.add(n)

        db.commit()
        print("✅ Base de datos poblada con éxito.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()

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

### FILE: `backend/app/services/evaluation/evlcr_service.py`

```
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
```

### FILE: `backend/app/services/evaluation/evlgt_service.py`

```
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
```

### FILE: `backend/app/services/agreement/agrgt_service.py`

```
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
```

### FILE: `backend/app/services/agreement/agrfn_service.py`

```
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRFN"

def handle_agrfn(data: str) -> str:
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
        if a.estado_acuerdo != EstadoAcuerdoEnum.aceptado:
            return f"{SERVICE_ID}-ERR:estado inválido"
        a.estado_acuerdo = EstadoAcuerdoEnum.finalizado_exitosamente
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrfn)
```

### FILE: `backend/app/services/agreement/agrrj_service.py`

```
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRRJ"

def handle_agrrj(data: str) -> str:
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
        if a.estado_acuerdo != EstadoAcuerdoEnum.propuesto:
            return f"{SERVICE_ID}-ERR:estado inválido"
        a.estado_acuerdo = EstadoAcuerdoEnum.rechazado
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrrj)
```

### FILE: `backend/app/services/agreement/agrcr_service.py`

```
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRCR"

def handle_agrcr(data: str) -> str:
    # data esperado: "proponente_id;receptor_id;pub_prop_id;pub_rec_id;descripcion"
    parts = data.split(";", 4)
    if len(parts) != 5:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        prop_id = int(parts[0])
        rec_id = int(parts[1])
        pub_prop = int(parts[2])
        pub_rec = int(parts[3])
        desc = parts[4]
    except ValueError:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    db = SessionLocal()
    try:
        agr = Acuerdo(
            proponente_usuario_id=prop_id,
            receptor_usuario_id=rec_id,
            publicacion_proponente_id=pub_prop,
            publicacion_receptor_id=pub_rec,
            descripcion_propuesta_proponente=desc,
            estado_acuerdo=EstadoAcuerdoEnum.propuesto
        )
        db.add(agr)
        db.commit()
        return f"{SERVICE_ID}-OK:{agr.acuerdo_id}"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:inserción fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrcr)
```

### FILE: `backend/app/services/agreement/agrac_service.py`

```
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Acuerdo, EstadoAcuerdoEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "AGRAC"

def handle_agrac(data: str) -> str:
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
        if a.estado_acuerdo != EstadoAcuerdoEnum.propuesto:
            return f"{SERVICE_ID}-ERR:estado inválido"
        a.estado_acuerdo = EstadoAcuerdoEnum.aceptado
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_agrac)
```

### FILE: `backend/app/services/notification/ntfrd_service.py`

```
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Notificacion
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "NTFRD"

def handle_ntfrd(data: str) -> str:
    # data esperado: "notificacion_id"
    try:
        nid = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        n = db.query(Notificacion).get(nid)
        if not n:
            return f"{SERVICE_ID}-ERR:no encontrado"
        n.estado_leido = True
        db.commit()
        return f"{SERVICE_ID}-OK"
    except SQLAlchemyError:
        db.rollback()
        return f"{SERVICE_ID}-ERR:actualización fallida"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_ntfrd)
```

### FILE: `backend/app/services/notification/ntfgt_service.py`

```
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
```

### FILE: `backend/app/services/conversation/cvlst_service.py`

```
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
```

### FILE: `backend/app/services/conversation/msgsn_service.py`

```
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
```

### FILE: `backend/app/services/conversation/msggt_service.py`

```
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
```

### FILE: `backend/app/services/conversation/cvnew_service.py`

```
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
```

### FILE: `backend/app/services/publication/pbget_service.py`

```
#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion

SERVICE_ID = "PBGET"

def handle_pbget(data: str) -> str:
    # data esperado: "publicacion_id"
    try:
        pid = int(data)
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        p = db.query(Publicacion).get(pid)
        if not p:
            return f"{SERVICE_ID}-ERR:no encontrado"
        cat = p.categoria.nombre_categoria if p.categoria else ""
        tags = ",".join(t.nombre_etiqueta for t in p.etiquetas)
        return (f"{SERVICE_ID}-OK:"
                f"{p.publicacion_id};{p.usuario_id};{p.tipo_publicacion.value};"
                f"{p.descripcion_habilidad};{cat};{tags}")
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbget)

```

### FILE: `backend/app/services/publication/pbncr_service.py`

```
#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion, Categoria, Etiqueta, TipoPublicacionEnum
from sqlalchemy.exc import SQLAlchemyError

SERVICE_ID = "PBNCR"

def handle_pbncr(data: str) -> str:
    # data esperado: "usuario_id;tipo;descripcion;categoria_id;et1,et2"
    parts = data.split(";")
    if len(parts) != 5:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        user_id = int(parts[0])
        tipo = TipoPublicacionEnum(parts[1])
        descripcion = parts[2]
        cat_id = int(parts[3])
    except Exception:
        return f"{SERVICE_ID}-ERR:datos inválidos"

    etiquetas = [e.strip() for e in parts[4].split(",") if e.strip()]
    db = SessionLocal()
    try:
        # validar categoría si viene
        if cat_id:
            cat = db.query(Categoria).get(cat_id)
            if not cat:
                return f"{SERVICE_ID}-ERR:categoria no encontrada"
        pub = Publicacion(
            usuario_id=user_id,
            tipo_publicacion=tipo,
            descripcion_habilidad=descripcion,
            categoria_id=cat_id or None
        )
        # administrar etiquetas
        for nombre in etiquetas:
            tag = db.query(Etiqueta).filter_by(nombre_etiqueta=nombre).first()
            if not tag:
                tag = Etiqueta(nombre_etiqueta=nombre)
            pub.etiquetas.append(tag)

        db.add(pub)
        db.commit()
        return f"{SERVICE_ID}-OK:{pub.publicacion_id}"
    except SQLAlchemyError as e:
        db.rollback()
        return f"{SERVICE_ID}-ERR:{e.__class__.__name__}"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbncr)

```

### FILE: `backend/app/services/publication/pblst_service.py`

```
#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion, Categoria, TipoPublicacionEnum
from sqlalchemy.orm import joinedload

SERVICE_ID = "PBLST"

def handle_pblst(data: str) -> str:
    # data esperado: "tipo;texto_busqueda"
    parts = data.split(";")
    if len(parts) != 2:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        tipo = TipoPublicacionEnum(parts[0])
        texto = parts[1]
    except Exception:
        return f"{SERVICE_ID}-ERR:tipo inválido"

    db = SessionLocal()
    try:
        pubs = (
            db.query(Publicacion)
              .options(joinedload(Publicacion.categoria), joinedload(Publicacion.etiquetas))
              .filter(
                  Publicacion.tipo_publicacion == tipo,
                  Publicacion.descripcion_habilidad.ilike(f"%{texto}%")
              )
              .all()
        )
        if not pubs:
            return f"{SERVICE_ID}-OK:"

        líneas = []
        for p in pubs:
            cat = p.categoria.nombre_categoria if p.categoria else ""
            tags = ",".join(t.nombre_etiqueta for t in p.etiquetas)
            # recortamos descripción para no saturar
            desc = p.descripcion_habilidad
            líneas.append(f"{p.publicacion_id};{p.usuario_id};{p.tipo_publicacion.value};"
                          f"{desc[:30]}…;{cat};{tags}")
        return f"{SERVICE_ID}-OK:" + "|".join(líneas)
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pblst)

```

### FILE: `backend/app/services/publication/pbdel_service.py`

```
#!/usr/bin/env python3
from app.services.utils import serve
from app.adapters.db import SessionLocal
from app.adapters.models import Publicacion

SERVICE_ID = "PBDEL"

def handle_pbdel(data: str) -> str:
    # data esperado: "usuario_id;publicacion_id"
    parts = data.split(";")
    if len(parts) != 2:
        return f"{SERVICE_ID}-ERR:formato inválido"
    try:
        user_id = int(parts[0])
        pub_id = int(parts[1])
    except ValueError:
        return f"{SERVICE_ID}-ERR:formato inválido"

    db = SessionLocal()
    try:
        p = db.query(Publicacion).get(pub_id)
        if not p:
            return f"{SERVICE_ID}-ERR:no encontrado"
        if p.usuario_id != user_id:
            return f"{SERVICE_ID}-ERR:prohibido"
        db.delete(p)
        db.commit()
        return f"{SERVICE_ID}-OK"
    finally:
        db.close()

if __name__ == "__main__":
    serve(SERVICE_ID, handle_pbdel)

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

### FILE: `frontend/index.html`

```
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Skilltrade App</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <div id="app">
    <!-- Secciones: login/register, perfil, publicaciones, chat, notificaciones -->
    <section id="auth">
      <h2>Iniciar Sesión / Registro</h2>
      <form id="login-form">
        <input type="email" id="login-email" placeholder="Email" required>
        <input type="password" id="login-pass" placeholder="Contraseña" required>
        <button type="submit">Entrar</button>
      </form>
      <form id="register-form">
        <input type="text" id="reg-name" placeholder="Usuario" required>
        <input type="email" id="reg-email" placeholder="Email" required>
        <input type="password" id="reg-pass" placeholder="Contraseña" required>
        <button type="submit">Registrar</button>
      </form>
    </section>

    <section id="profile" class="hidden">
      <h2>Perfil</h2>
      <div id="profile-info"></div>
      <button id="logout-btn">Cerrar Sesión</button>
    </section>

    <section id="posts" class="hidden">
      <h2>Publicaciones</h2>
      <div id="posts-list"></div>
    </section>

    <section id="chat" class="hidden">
      <h2>Chat</h2>
      <div id="conversations"></div>
      <div id="messages"></div>
      <form id="message-form">
        <input type="text" id="message-input" placeholder="Escribe tu mensaje..." required>
        <button type="submit">Enviar</button>
      </form>
    </section>

    <section id="notifications" class="hidden">
      <h2>Notificaciones</h2>
      <ul id="notifications-list"></ul>
    </section>
  </div>

  <script src="js/app.js"></script>
</body>
</html>
```

### FILE: `frontend/js/app.js`

```
const WS_URL = 'ws://localhost:8000/ws';
const PREFIX_LEN = 5;
let ws;
let currentUser;
let currentConvId;

function connect() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => console.log('WebSocket conectado');
  ws.onmessage = ({ data }) => handleResponse(data);
  ws.onerror = e => console.error('WS Error:', e);
}

function sendTx(service, payload) {
  return new Promise((resolve, reject) => {
    const body = service + payload;
    const prefix = String(body.length).padStart(PREFIX_LEN, '0');
    ws.send(prefix + body);
    ws.addEventListener('message', function handler(evt) {
      const msg = evt.data;
      ws.removeEventListener('message', handler);
      resolve(msg);
    });
  });
}

function parseMsg(msg) {
  const length = parseInt(msg.slice(0, PREFIX_LEN));
  const serv = msg.slice(PREFIX_LEN, PREFIX_LEN+5);
  const rest = msg.slice(PREFIX_LEN+5);
  return { serv, rest };
}

async function login(email, pass) {
  const resp = await sendTx('USLOG', `${email};${pass}`);
  const { serv, rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const [id, name] = rest.split(':')[1].split(';');
    currentUser = { id, name };
    showProfile();
  } else alert('Error: ' + rest);
}

async function register(name, email, pass) {
  const resp = await sendTx('USREG', `${name};${email};${pass}`);
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) alert('Registrado con ID ' + rest.split(':')[1]);
  else alert('Error: ' + rest);
}

async function loadProfile() {
  const resp = await sendTx('USGET', currentUser.id);
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const data = rest.split(':')[1].split(';');
    document.getElementById('profile-info').innerText =
      `ID: ${data[0]}\nUsuario: ${data[1]}\nEmail: ${data[2]}\nReputación: ${data[3]}`;
  }
}

async function loadPosts() {
  const resp = await sendTx('PBLST', 'oferta;');
  const { rest } = parseMsg(resp);
  if (rest.startsWith('OK')) {
    const list = rest.slice(3).split('|');
    const container = document.getElementById('posts-list');
    container.innerHTML = '';
    list.forEach(item => {
      if (!item) return;
      const parts = item.split(';');
      const card = document.createElement('div'); card.className = 'card';
      card.innerHTML = `<strong>${parts[2]}</strong><br>${parts[3]}`;
      container.appendChild(card);
    });
  }
}

// Eventos de formularios
window.onload = () => {
  connect();
  document.getElementById('login-form').onsubmit = e => {
    e.preventDefault();
    login(
      e.target['login-email'].value,
      e.target['login-pass'].value
    );
  };
  document.getElementById('register-form').onsubmit = e => {
    e.preventDefault();
    register(
      e.target['reg-name'].value,
      e.target['reg-email'].value,
      e.target['reg-pass'].value
    );
  };
  document.getElementById('logout-btn').onclick = () => location.reload();
};

// Navegación básica entre secciones
function showProfile() {
  ['auth'].forEach(i => document.getElementById(i).classList.add('hidden'));
  ['profile','posts','chat','notifications'].forEach(i => document.getElementById(i).classList.remove('hidden'));
  loadProfile();
  loadPosts();
}
```

### FILE: `frontend/css/style.css`

```
body {
  font-family: Arial, sans-serif;
  margin: 0;
  padding: 1rem;
  background: #f5f5f5;
}
.hidden { display: none; }
section { margin-bottom: 2rem; background: #fff; padding: 1rem; border-radius: 4px; }
input, button { margin: 0.5rem 0; padding: 0.5rem; width: 100%; box-sizing: border-box; }
#posts-list .card { border: 1px solid #ddd; padding: 0.5rem; margin-bottom: 0.5rem; border-radius: 4px; }
#conversations, #notifications-list { list-style: none; padding: 0; }
#conversations .conv-item, #notifications-list li { border-bottom: 1px solid #eee; padding: 0.5rem; cursor: pointer; }
#messages { max-height: 200px; overflow-y: auto; margin-bottom: 0.5rem; }
#messages .msg { margin-bottom: 0.5rem; }
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

