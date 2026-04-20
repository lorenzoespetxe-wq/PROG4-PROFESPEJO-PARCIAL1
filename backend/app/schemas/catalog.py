from sqlmodel import SQLModel

# Anotaciones de tipo de Python
# para definir campos opcionales y listas.
from typing import Optional, List

# Para las marcas de tiempo de auditoría
from datetime import datetime

# Para las validaciones antes de interactuar con la DB
from pydantic import Field

# ESQUEMAS BASE:
# con los atributos comunes que se utilizaran tanto para recibir
# como para enviar datos. Ninguno incluye ni el ID ni los campos
# de auditoría, si incluyen todo lo demás.


class CategoriaBase(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    imagen_url: Optional[str] = None
    parent_id: Optional[int] = None


class IngredienteBase(SQLModel):
    nombre: str = Field(max_length=100)
    descripcion: Optional[str] = None
    es_alergeno: bool = False


class ProductoBase(SQLModel):
    nombre: str = Field(max_length=150)
    descripcion: Optional[str] = None
    imagenes_url: List[str] = []
    precio_base: float = Field(ge=0.0)  # ge=0 es >= 0.0
    stock_cantidad: int = Field(default=0, ge=0)  # >= 0
    disponible: bool = True
    # ge es greater or equal, valida en python que el
    # precio y el stock no sean negativos.


# ESQUEMAS DE ENTRADA:
# atributos necesarios para los insert / update.


class CategoriaCreate(CategoriaBase):
    pass  # es igual al base


class IngredienteCreate(IngredienteBase):
    pass  # es igual al base


class ProductoCreate(ProductoBase):
    # Productos necesitará que le demos al menos 1 id de categoria
    # y podemos darle los ids de los ingredientes.
    categoria_ids: List[int] = Field(min_length=1)
    ingrediente_ids: List[int] = []


# ESQUEMAS DE SALIDA:
# Atributos que nos devolverá al leer. Son iguales a los base,
# pero incluyen campos de creación y update, así como los ids.


class CategoriaRead(CategoriaBase):
    id: int
    created_at: datetime
    updated_at: datetime
    # nos da id y campos de auditoría


class IngredienteRead(IngredienteBase):
    id: int
    created_at: datetime
    updated_at: datetime


class ProductoRead(ProductoBase):
    id: int
    created_at: datetime
    updated_at: datetime


# LECTURA DETALLADA DE PRODUCTO:


class ProductoReadWithDetails(ProductoRead):
    # Incluye esta vez la lista de categorías y de ingredientes.
    categorias: List[CategoriaRead] = []
    ingredientes: List[IngredienteRead] = []
