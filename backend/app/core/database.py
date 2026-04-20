# Importamos clases fundamentales de SQLModel.
# create_engine gestiona la conexión con la DB
# Session las operaciones CRUD individuales
from sqlmodel import create_engine

# Connection String con Postgres
DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/parcial_db"

# Instanciamos el motor de la DB
engine = create_engine(DATABASE_URL, echo=True)
