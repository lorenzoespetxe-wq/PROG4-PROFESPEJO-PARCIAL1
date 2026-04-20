# Herramientas de FastAPI para construir rutas, inyectar
# dependencias lanzar excepciones y validar URLs
from fastapi import APIRouter, Depends, HTTPException, Query, Path, status

# Session para interactuar con la DB, y select para consultas SQL
from sqlmodel import Session, select

#
from typing import List, Annotated

# Función para conectar con la DB en las peticiones
from app.core.database import get_session

# Importamos los modelos
from app.models.catalog import (
    Producto,
    Categoria,
    Ingrediente,
    ProductoCategoria,
    ProductoIngrediente,
)

# y los esquemas
from app.schemas.catalog import ProductoCreate, ProductoRead, ProductoReadWithDetails

# Instanciamos el enrutador, todas con el prefijo /productos
router = APIRouter(prefix="/productos", tags=["Productos"])


# 1 - RUTA DE GET ALL con response_model
# La salida será una lista de de objetos con el esquema ProductoRead
@router.get("/", response_model=List[ProductoRead])
def read_productos(  # definimos funcion de lectura
    session: Annotated[Session, Depends(get_session)],  # inyecta la sesión
    offset: int = 0,  # empezamos desde el registro 0
    limit: Annotated[int, Query(le=100)] = 10,  # máximo 100 registros, trae de a 10
):
    # consulta SQL con SQLModel, aplica filtros de paginación, trae todos los resultados.
    productos = session.exec(select(Producto).offset(offset).limit(limit)).all()
    return productos


# 2 - RUTA DE GET con response_model, esta vez recibe un id,
# y devuelve un objeto con el esquema ProductoConDetalles
# que incluye también la lista de categorías y de ingredientes.
@router.get("/{producto_id}", response_model=ProductoReadWithDetails)
def read_producto(  # definimos función
    producto_id: Annotated[
        int, Path(title="ID del producto")
    ],  # recibe el ID, Path hace que sea obligatorio que venga de la URL
    session: Annotated[Session, Depends(get_session)],  # inyecta la sesión
):
    # Buscamos el producto desde la DB con el ID
    producto = session.get(Producto, producto_id)
    if not producto:  # si no lo encuentra
        raise HTTPException(  # tiramos una excepcion 404 con este detalle  v v v
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )
    return producto  # devuelve el producto si lo encontro


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
    session: Annotated[Session, Depends(get_session)],  # inyecta la sesión
):

    # Instanciamos un Producto al que le tranferimos los datos del
    # modelo validado. Por el momento sin los ID de relaciones.
    producto_db = Producto(
        nombre=producto_in.nombre,
        descripcion=producto_in.descripcion,
        imagenes_url=producto_in.imagenes_url,
        precio_base=producto_in.precio_base,
        stock_cantidad=producto_in.stock_cantidad,
        disponible=producto_in.disponible,
    )

    session.add(producto_db)  # preaparamos para guardar el registro
    session.commit()  # guardamos el registro
    session.refresh(producto_db)  # refrescamos y obtenemos el ID autogenerado

    # a - INCULAMOS CATEGORÍAS (relación muchos a muchos)
    categorias = session.exec(  # inicia la ejecución de una consulta
        # trae las categorías cuyo id este en la lista del producto que subimos
        select(Categoria).where(Categoria.id.in_(producto_in.categoria_ids))
    ).all()  # transforma el resultado en un objeto de python

    # Compara lo que encontro en la DB con los ID que le pasamos al producto
    if len(categorias) != len(producto_in.categoria_ids):
        raise HTTPException(  # si es distinto tira un excepcio 400
            status_code=status.HTTP_400_BAD_REQUEST,  # y dice v v v
            detail="Una o más categorías no existen en la BD",
        )

    # por categoría en categorias
    for i, cat in enumerate(categorias):
        # instancia el vinculo con la tabla intermedia
        link_cat = ProductoCategoria(
            producto_id=producto_db.id,  # carga id de producto
            categoria_id=cat.id,  # y el id de categoria
            # el primer elemento de la lista de categorias se pone como principal
            es_principal=(i == 0),
        )
        # prepara para guardar el registro en la tabla intermedia
        session.add(link_cat)

    # b - VINCULAR LOS INGREDIENTES (muchos a muchos)
    # Acá empezamos con una clausula if, porque no es obligatorio
    # que nos pasaran un ID de ingrediente
    # El resto de la lógica es igual.
    if producto_in.ingrediente_ids:
        ingredientes = session.exec(
            select(Ingrediente).where(Ingrediente.id.in_(producto_in.ingrediente_ids))
        ).all()
        if len(ingredientes) != len(producto_in.ingrediente_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más ingredientes no existen en la BD",
            )

        for ing in ingredientes:
            link_ing = ProductoIngrediente(
                producto_id=producto_db.id, ingrediente_id=ing.id
            )
            # prepara el registro en la tabla intermedia
            session.add(link_ing)

    # Los registros ya estan preparados
    session.commit()  # guardamos los registros
    session.refresh(producto_db)

    return producto_db  # Devuelve el producto con las relaciones cargadas


# 4 - RUTA DE DELETE, sin response_model, porque la función devuelve None.
# Devuelve 204 con un borrado exitoso.
@router.delete("/{producto_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_producto(  # definimos funcion
    producto_id: int,  # recibe id a borrar
    session: Annotated[Session, Depends(get_session)],  # inyecta sesión
):
    # Busca el producto x id
    producto = session.get(Producto, producto_id)
    if not producto:  # si no o encuentra
        raise HTTPException(  # tira excepción 404 y el detalle v v v
            status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado"
        )

    session.delete(producto)  # prepara para borrar
    session.commit()  # borra
