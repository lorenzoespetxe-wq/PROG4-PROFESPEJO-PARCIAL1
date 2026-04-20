from fastapi import FastAPI
from app.api import categorias, productos, ingredientes
from app.core.database import engine
from sqlmodel import SQLModel

# Instanciamos la aplicación
app = FastAPI(title="Parcial 1 - Programación IV")


# Define un evento cuando se ejecuta el servidor Uvicorn
@app.on_event("startup")
def on_startup():
    # crea todas las tablas definidas en los modelos
    SQLModel.metadata.create_all(engine)


# Registramos las rutas del módulo categorías con el
# prefijo /api para modularizar los endpoints
app.include_router(categorias.router, prefix="/api")
# same with productos
app.include_router(productos.router, prefix="/api")
# same with ingredientes
app.include_router(ingredientes.router, prefix="/api")


# Endpoint de prueba para ver que el back esta en linea
@app.get("/")
def root():
    return {"message": "API Fullstack funcionando"}
