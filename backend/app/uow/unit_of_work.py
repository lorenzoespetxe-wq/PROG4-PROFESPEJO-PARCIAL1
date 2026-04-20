# Se trae Session para inyectar sesiones e interactuar la db
# y engine que trae la configuración de la conexión con la misma.
from sqlmodel import Session
from app.core.database import engine

# El patron de UoW e usa para garantizar que un conjunto de operaciones en la DB
# se traten como una única transacción atómica. Si una operación fall, ninguna se guarda.
# Esto es para evitar que la DB quede en un estado inconsistente, con modificaciones
# parciales. También centraliza la gestión del ciclo de vida de la sesión (abriendola y cerrandola)
# liberando a ls clases service de esa responsabilidad técnica.


class UnitOfWork:
    def __init__(self):
        self.session: Session = None  # inicializa el atributo session en None

    def __enter__(self):  # cuando se usa la instrucción with UnitOfWork()
        self.session = Session(engine)  # crea una instancia de Session
        return self  # se devuelve a si misma

    def __exit__(
        self, exc_type, exc_val, traceback
    ):  # se ejecuta al salir de el bloque with UnitOfWork()
        if (
            exc_type is not None
        ):  # si el codigo dentro del bloque lanzo alguna excepcion
            self.session.rollback()  # hace un rollback y deshace los cambios pendientes
        self.session.close()  # siempre cierra la conexion al final

    def commit(self):  # metodo que confirma cambios
        self.session.commit()

    def rollback(self):  # metodo que revierte cambios
        self.session.rollback()
