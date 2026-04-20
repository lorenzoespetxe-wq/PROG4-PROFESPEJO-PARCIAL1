from sqlmodel import SQLModel, Field, Relationship, Column, DECIMAL, String
from sqlalchemy import DateTime, func, CheckConstraint, Integer
from sqlalchemy.dialects.postgresql import ARRAY
from typing import Optional, List
from datetime import datetime


# Definimos tabla intermedia ProductoCategoria
class ProductoCategoria(SQLModel, table=True):
    # Las FK tienen que ser optional en Python aunque sean obligatorias
    # en SQL porque sino Pyhton te obligaría a pasar los IDs al crear
    # el objeto. Así la base de dato asigna los IDs después.

    # 2 ids para PK compuesta
    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    categoria_id: Optional[int] = Field(
        default=None, foreign_key="categoria.id", primary_key=True
    )
    # Indica si es la categoria primaria del producto
    es_principal: bool = Field(default=False)
    # Fecha de creación del registro
    created_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True), server_default=func.now(), nullable=False
        )
    )


# Definimos tabla intermedia PorductoIngrediente
class ProductoIngrediente(SQLModel, table=True):
    # 2 ids para PK compuesta
    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    ingrediente_id: Optional[int] = Field(
        default=None, foreign_key="ingrediente.id", primary_key=True
    )
    # ¿Podemos removerlo? Booleano, default falso.
    es_removible: bool = Field(default=False)


# Definimos tabla categoría
class Categoria(SQLModel, table=True):
    # PK, opcional porque lo mete la DB
    id: Optional[int] = Field(default=None, primary_key=True)
    # Nombre, 100 caracteres max, no nu nulo, único
    nombre: str = Field(index=True, unique=True, max_length=100)
    # Descripción, string
    descripcion: Optional[str] = Field(default=None)
    # URL de imagen, string
    imagen_url: Optional[str] = Field(default=None)
    # ID de categoría padre, FK, puede ser nulo
    parent_id: Optional[int] = Field(default=None, foreign_key="categoria.id")
    # Fecha de creación
    created_at: datetime = (
        Field(  # NO NULO, mapea a TIMESTAMPTZ, se genera en el INSERT
            sa_column=Column(
                DateTime(timezone=True), server_default=func.now(), nullable=False
            )
        )
    )
    # Fecha de actualizacion
    updated_at: datetime = (
        Field(  # Igual que el de creación, pero se actualiza con los UDPATE
            sa_column=Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )
        )
    )
    # Fecha de borrado
    deleted_at: Optional[datetime] = Field(  # Puede ser nulo, se llenará al eliminarse
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    # Definimos una colección de objetos Producto
    productos: List["Producto"] = Relationship(
        # back_populates permite que al actualizar un producto,
        # la categoría refleje el cambio también.
        # link_model especifica la tabla intermedia.
        back_populates="categorias",
        link_model=ProductoCategoria,
    )


# Definimos tabla Ingrediente
class Ingrediente(SQLModel, table=True):
    # ID, opcional por que lo mete la DB
    id: Optional[int] = Field(default=None, primary_key=True)
    # Nombre, 100 caracteres max, no nulo, único
    nombre: str = Field(unique=True, max_length=100)
    # Descripción, string
    descripcion: Optional[str] = None
    # ¿Es un alérgeno? Booleano, default falso.
    es_alergeno: bool = Field(default=False)
    # Fecha de creación
    created_at: datetime = (
        Field(  # NO NULO, mapea a TIMESTAMPTZ, se genera en el INSERT
            sa_column=Column(
                DateTime(timezone=True), server_default=func.now(), nullable=False
            )
        )
    )
    # Fecha de actualizacion
    updated_at: datetime = (
        Field(  # Igual que el de creación, pero se actualiza con los UDPATE
            sa_column=Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )
        )
    )
    # Definimos una colección de objetos Producto
    productos: List["Producto"] = Relationship(
        # configurado igual que categoría con producto
        back_populates="ingredientes",
        link_model=ProductoIngrediente,
    )


# Definimos tabla Producto
class Producto(SQLModel, table=True):
    # ID, opcional por que lo mete la DB
    id: Optional[int] = Field(default=None, primary_key=True)
    # Nombre, 150 caracteres max, no nulo
    nombre: str = Field(max_length=150)
    # Descripción, string
    descripcion: Optional[str] = None
    # URL de imagenes, array de strings
    imagenes_url: List[str] = Field(default=[], sa_column=Column(ARRAY(String)))
    # Precio, float con 2 decimales, hasta 10 digitos
    precio_base: float = Field(
        sa_column=Column(DECIMAL(10, 2), CheckConstraint("precio_base >= 0"))
    )
    # Stock, entero, deafault 0.
    stock_cantidad: int = Field(
        default=0, sa_column=Column(Integer, CheckConstraint("stock_cantidad >= 0"))
    )
    # ¿Está disponible? Booleanom default verdadero
    disponible: bool = Field(default=True)
    # Fecha de creación
    created_at: datetime = (
        Field(  # NO NULO, mapea a TIMESTAMPTZ, se genera en el INSERT
            sa_column=Column(
                DateTime(timezone=True), server_default=func.now(), nullable=False
            )
        )
    )
    # Fecha de actualizacion
    updated_at: datetime = (
        Field(  # Igual que el de creación, pero se actualiza con los UDPATE
            sa_column=Column(
                DateTime(timezone=True),
                server_default=func.now(),
                onupdate=func.now(),
                nullable=False,
            )
        )
    )
    # Fecha de borrado
    deleted_at: Optional[datetime] = Field(  # Puede ser nulo, se llenará al eliminarse
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    # Lista de categorías a las que pertence, e ingredientes que incluye
    # También configurados con back_populates y señalando las tablas
    # intermedias.
    categorias: List[Categoria] = Relationship(
        back_populates="productos", link_model=ProductoCategoria
    )
    ingredientes: List[Ingrediente] = Relationship(
        back_populates="productos", link_model=ProductoIngrediente
    )
