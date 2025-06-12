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
