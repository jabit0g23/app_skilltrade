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
