from fastapi import APIRouter, Query, Path, status
from typing import List, Annotated

from app.schemas.catalog import IngredienteRead, IngredienteCreate, IngredienteUpdate
from app.services.ingrediente_service import IngredienteService

# Instanciamos el enrutador, prefix evita repetir "/ingredientes" en cada ruta
router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


# 1 - RUTA GET ALL con response_model de IngredienteRead,
# que incluye id y campos de auditoría.
@router.get("/", response_model=List[IngredienteRead])
def read_ingredientes(  # funcion de lectura
    offset: int = 0,  # trae desde el primer registro
    limit: Annotated[int, Query(le=100)] = 10,  # maximo 100 registros, solo trae 10
):
    # Delega la consulta paginada al servicio
    return IngredienteService.get_all(offset=offset, limit=limit)


# 2 - RUTA GET con id, con response_model, también esquema IngredienteRead
@router.get("/{ingrediente_id}", response_model=IngredienteRead)
def read_ingrediente(  # función de lectura
    # recibe el ID, Path hace que sea obligatorio que venga de la URL
    ingrediente_id: Annotated[int, Path(title="ID del ingrediente")],
):
    # Delega la busqueda al servicio
    return IngredienteService.get_by_id(ingrediente_id=ingrediente_id)


# 3 - RUTA POST con response_model, define 201 como respuesta exitosa
@router.post("/", response_model=IngredienteRead, status_code=status.HTTP_201_CREATED)
def create_ingrediente(  # funcion de creacion, recibe los datos de la petición
    ingrediente_in: IngredienteCreate,
):
    # Delega la creación al servicio
    return IngredienteService.create(ingrediente_in=ingrediente_in)


# 4 - RUTA PATCH (UPDATE parcial) con response_model (mismo de arriba)
@router.patch("/{ingrediente_id}", response_model=IngredienteRead)
def update_ingrediente(  # definimos funcion
    ingrediente_id: int,  # recibe un id para ver cual actualizamos
    ingrediente_in: IngredienteUpdate,  # recibe los campos del esquema IngredienteUpdate
):
    # Delega la actualización al servicio
    return IngredienteService.update(
        ingrediente_id=ingrediente_id, ingrediente_in=ingrediente_in
    )


# 5 - RUTA DELETE, sin response_model, porque la función devuelve None.
# Devuelve 204 con un borrado exitoso.
@router.delete("/{ingrediente_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ingrediente(  # definimos funcion
    ingrediente_id: int,  # recibimos el id a borrar
):
    # Delega la eliminación al servicio
    IngredienteService.delete(ingrediente_id=ingrediente_id)
