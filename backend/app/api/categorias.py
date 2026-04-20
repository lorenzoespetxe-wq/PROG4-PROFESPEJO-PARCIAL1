from fastapi import APIRouter, Query, Path, status
from typing import List, Annotated

from app.services.categoria_service import CategoriaService
from app.schemas.catalog import CategoriaRead, CategoriaCreate, CategoriaUpdate

# Instanciamos el enrutador, prefix evita repetir "/categorias" en
# cada ruta de los decoradores de las funciones
router = APIRouter(prefix="/categorias", tags=["Categorias"])


# 1 - RUTA GET ALL con response_model de LeerCategoria,
# que incluye id y campos de auditoría.
@router.get("/", response_model=List[CategoriaRead])
def read_categorias(  # funcion de lectura
    offset: int = 0,  # trae desde el primer registro
    limit: Annotated[int, Query(le=100)] = 10,  # maximo 100 registros, solo trae 10
):
    # Delega la consulta paginada al servicio
    return CategoriaService.get_all(offset=offset, limit=limit)


# 2 - RUTA GET con id, con response_model, también esquema LeerCategoría
@router.get("/{categoria_id}", response_model=CategoriaRead)
def read_categoria(  # función de lectura
    # recibe el ID, Path hace que sea obligatorio que venga de la URL
    categoria_id: Annotated[int, Path(title="ID de la categoría")],
):
    # Delega la busqueda al servicio
    return CategoriaService.get_by_id(categoria_id=categoria_id)


# 3 - RUTA POST con response_model, define 201 como respuesta exitosa
@router.post("/", response_model=CategoriaRead, status_code=status.HTTP_201_CREATED)
def create_categoria(  # funcion de creacion, recibe los datos de la petición
    categoria_in: CategoriaCreate,
):
    # Delega la creación al servicio
    return CategoriaService.create(categoria_in=categoria_in)


# 4 - RUTA PATCH (UPDATE parcial) con response_model (mismo de arriba)
@router.patch("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(  # definimos funcion
    categoria_id: int,  # recibe un id para ver cual actualizamos
    categoria_in: CategoriaUpdate,  # recibe los campos del esquema ActualizarCategoria
):
    # Delega la actualización al servicio
    return CategoriaService.update(categoria_id=categoria_id, categoria_in=categoria_in)


# 5 - RUTA DELETE, sin response_model, porque la función devuelve None.
# Devuelve 204 con un borrado exitoso.
@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_categoria(  # definimos funcion
    categoria_id: int,  # recibimos el id a borrar
):
    # Delega la eliminación al servicio
    CategoriaService.delete(categoria_id=categoria_id)
