from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select
from typing import List, Annotated
from app.core.database import get_session
from app.models.catalog import Categoria
from app.schemas.catalog import CategoriaRead, CategoriaCreate

# Instanciamos el enrutador, prefix evita repetir "/categorias" en
# cada ruta de los decoradores de las funciones
router = APIRouter(prefix="/categorias", tags=["Categorias"])


# Define ruta de GET con response_model
@router.get("/", response_model=List[CategoriaRead])
def read_categorias(  # funcion de lectura
    session: Annotated[Session, Depends(get_session)],  # inyecta una sesion
    offset: int = 0,  # trae desde el primer registro
    limit: Annotated[int, Query(le=100)] = 10,  # maximo 100 registros, solo trae 10
):
    # consulta SQL con SQLModel, aplica filtros de paginación, trae rodos los resultados.
    categorias = session.exec(select(Categoria).offset(offset).limit(limit)).all()
    return categorias


# Define ruta de POST con response_model, define 201 como respuesta exitosa
@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def create_categoria(  # funcion de creacion, recibe los datos de la petición
    categoria_in: CategoriaCreate,
    session: Annotated[Session, Depends(get_session)],  # e inyecta una sesión
):
    categoria_db = Categoria(**categoria_in.model_dump())
    session.add(categoria_db)  # prepara para guardar el registro
    session.commit()  # guarda el registro
    session.refresh(categoria_db)  # actualiza el objeto para mostrar el id autogenerado
    return categoria_db  # devuelve el objeto cread


# El CRUD no esta completo, ver si es necesario.
