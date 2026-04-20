from fastapi import APIRouter, Depends, HTTPException, Query, Path, status
from sqlmodel import Session, select
from typing import List, Annotated
from app.core.database import get_session
from app.models.catalog import Categoria
from app.schemas.catalog import CategoriaRead, CategoriaCreate, CategoriaUpdate

# Instanciamos el enrutador, prefix evita repetir "/categorias" en
# cada ruta de los decoradores de las funciones
router = APIRouter(prefix="/categorias", tags=["Categorias"])


# 1 - RUTA GET ALL con response_model de LeerCategoria,
# que incluye id y campos de auditoría.
@router.get("/", response_model=List[CategoriaRead])
def read_categorias(  # funcion de lectura
    session: Annotated[Session, Depends(get_session)],  # inyecta una sesion
    offset: int = 0,  # trae desde el primer registro
    limit: Annotated[int, Query(le=100)] = 10,  # maximo 100 registros, solo trae 10
):
    # consulta SQL con SQLModel, aplica filtros de paginación, trae rodos los resultados.
    categorias = session.exec(select(Categoria).offset(offset).limit(limit)).all()
    return categorias


# 2 - RUTA GET con id, con response_model, también esquema LeerCategoría
@router.get("/{categoria_id}", response_model=CategoriaRead)
def read_categoria(  # función de lectura
    # recibe el ID, Path hace que sea obligatorio que venga de la URL
    categoria_id: Annotated[int, Path(title="ID de la categoría")],
    session: Annotated[Session, Depends(get_session)],  # inyecta una sesión
):
    # Buscamos el producto desde la DB con el ID
    categoria = session.get(Categoria, categoria_id)
    if not categoria:  # si no existe
        raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )
    return categoria  # devolvemos la categoría


# 3 - RUTA POST con response_model, define 201 como respuesta exitosa
@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def create_categoria(  # funcion de creacion, recibe los datos de la petición
    categoria_in: CategoriaCreate,
    session: Annotated[Session, Depends(get_session)],  # e inyecta una sesión
):
    # Pydantic transforma el objeto categoria_in (de forma CategoriaCreate)
    # en un diccionario estadar de python usando .model_dump()
    # Los "**" hacen el desempaquetado de los pares clave valor
    # a argumentos para armar un objeto del modelo Categoria y guardarlo
    # categoria_db.
    categoria_db = Categoria(**categoria_in.model_dump())
    session.add(categoria_db)  # prepara para guardar el registro
    session.commit()  # guarda el registro
    session.refresh(categoria_db)  # actualiza el objeto para mostrar el id autogenerado
    return categoria_db  # devuelve el objeto cread


# 4 - RUTA PATCH (UPDATE parcial) con response_model (mismo de arriba)
@router.patch("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(  # definimos funcion
    categoria_id: int,  # recibe un id para ver cual actualizamos
    categoria_in: CategoriaUpdate,  # recibe los campos del esquema ActualizarCategoria
    session: Annotated[Session, Depends(get_session)],  # inyecta sesión
):
    # Buscamos la categoria en la DB
    db_cat = session.get(Categoria, categoria_id)
    if not db_cat:  # si no la encontramos
        raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )

    # Convierte el objeto categoria_in de pydantic en un diccionario de Python
    # exclude_unset=True hace que el diccionario solo incluya los campos
    # que efectivamente envió el usuario. Lo guarda en cat_data.
    # Los otros clave valor (no enviados) no se incluirán.
    cat_data = categoria_in.model_dump(exclude_unset=True)

    for key, value in cat_data.items():  # Para cada clave valor en cat_data
        setattr(db_cat, key, value)  # en db_cat, por key se reemplazan los values

    session.add(db_cat)  # preparamos para guardar registo
    session.commit()  # guarda el registro
    session.refresh(db_cat)  # refresca el registro
    return db_cat  # devuelve el registro


# 5 - RUTA DELETE, sin response_model, porque la función devuelve None.
# Devuelve 204 con un borrado exitoso.
@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(  # definimos funcion
    categoria_id: int,  # recibimos el id a borrar
    session: Annotated[Session, Depends(get_session)],  # inyectamos sesión
):
    # Buscamos el registro en la DB
    categoria = session.get(Categoria, categoria_id)
    if not categoria:  # si no lo encontramos
        raise HTTPException(  # lanzamos excepción 404 con el detalle v v v
            status_code=status.HTTP_404_NOT_FOUND, detail="Categoría no encontrada"
        )

    session.delete(categoria)  # prepara para borrar
    session.commit()  # borra
