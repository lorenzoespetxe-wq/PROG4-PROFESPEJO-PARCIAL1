# Herramientas de FastAPI para construir rutas, inyectar
# dependencias lanzar excepciones y validar URLs
from fastapi import APIRouter, Query, Path, status
from typing import List, Annotated

# Importamos el servicio que maneja la lógica y la DB
from app.services.producto_service import ProductoService

# y los esquemas
from app.schemas.catalog import (
    ProductoCreate,
    ProductoRead,
    ProductoReadWithDetails,
    ProductoUpdate,
)

# Instanciamos el enrutador, todas con el prefijo /productos
router = APIRouter(prefix="/productos", tags=["Productos"])


# 1 - RUTA DE GET ALL con response_model
# La salida será una lista de de objetos con el esquema ProductoRead
@router.get("/", response_model=List[ProductoRead])
def read_productos(  # definimos funcion de lectura
    offset: int = 0,  # empezamos desde el registro 0
    limit: Annotated[int, Query(le=100)] = 10,  # máximo 100 registros, trae de a 10
):
    # Delega la consulta paginada al servicio
    return ProductoService.get_all(offset=offset, limit=limit)


# 2 - RUTA DE GET con response_model, esta vez recibe un id,
# y devuelve un objeto con el esquema ProductoConDetalles
# que incluye también la lista de categorías y de ingredientes.
@router.get("/{producto_id}", response_model=ProductoReadWithDetails)
def read_producto(  # definimos función
    producto_id: Annotated[
        int, Path(title="ID del producto")
    ],  # recibe el ID, Path hace que sea obligatorio que venga de la URL
):
    # Delega la busqueda al servicio
    return ProductoService.get_by_id(producto_id=producto_id)


# 3 - RUTA DE POST con response_model, siguiendo
# tambien el esquema de ProductoConDetalles.
# Si la operación es exitosa devuelve HTTP 201.
@router.post(
    "/", response_model=ProductoReadWithDetails, status_code=status.HTTP_201_CREATED
)
def create_producto(  # definimos función
    # recibe un objeto con con el Esquema ProductoCreate,
    # requiere al menos 1 ID de categoría, y puede recibir
    # IDs de ingredientes
    producto_in: ProductoCreate,
):
    # Delega la creación atómica al servicio
    return ProductoService.create(producto_in=producto_in)


# 4 - RUTA PATCH (UPDATE parcial) con response_model, mismo esquema.
@router.patch("/{producto_id}", response_model=ProductoReadWithDetails)
def update_producto(  # definimos función
    producto_id: int,  # recibimos id que vamos a actualizar
    producto_in: ProductoUpdate,  # recibimos los campos a actualizar, en el esquema ActualizarProducto
):
    # Delega la actualización atómica al servicio
    return ProductoService.update(producto_id=producto_id, producto_in=producto_in)


# 5 - RUTA DE DELETE, sin response_model, porque la función devuelve None.
# Devuelve 204 con un borrado exitoso.
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(  # definimos funcion
    producto_id: int,  # recibe id a borrar
):
    # Delega la eliminación al servicio
    ProductoService.delete(producto_id=producto_id)
