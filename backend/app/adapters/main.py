from fastapi import FastAPI
from .db import engine
from . import models

app = FastAPI()

# Esto ejecuta CREATE TABLE ... si no existe
models.Base.metadata.create_all(bind=engine)

# Aquí registras tus rutas REST y WebSockets
