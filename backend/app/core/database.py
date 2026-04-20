# Importamos clases fundamentales de SQLModel.
# create_engine gestiona la conexión con la DB
# Session las operaciones CRUD individuales
from sqlmodel import create_engine, Session

# Generator permite anotar el tipo de retorno
# de las funciones que provee la Sesión en la DB
from typing import Generator

# Connection String con Postgres
DATABASE_URL = "postgresql://admin:adminpassword@localhost:5432/parcial_db"

# Instanciamos el motor de la DB
engine = create_engine(DATABASE_URL, echo=True)


# definimos get_session para inyectarla despues como dependencia en los endpoints
def get_session() -> Generator[Session, None, None]:
    # with inicializa la sesión cuando se abre el bloque
    # y la cierra cuando se sale del mismo
    with Session(engine) as session:
        yield session
