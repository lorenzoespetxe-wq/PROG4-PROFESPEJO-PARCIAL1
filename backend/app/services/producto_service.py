from fastapi import HTTPException, status
from sqlmodel import select, delete
from app.uow.unit_of_work import UnitOfWork
from app.models.catalog import (
    Producto,
    Categoria,
    Ingrediente,
    ProductoCategoria,
    ProductoIngrediente,
)
from app.schemas.catalog import ProductoCreate, ProductoUpdate


class ProductoService:
    @staticmethod
    def get_all(offset: int, limit: int):
        with UnitOfWork() as uow:
            # consulta SQL con SQLModel, aplica filtros de paginación, trae todos los resultados.
            productos = uow.session.exec(
                select(Producto).offset(offset).limit(limit)
            ).all()
            return productos

    @staticmethod
    def get_by_id(producto_id: int):
        with UnitOfWork() as uow:
            # Buscamos el producto desde la DB con el ID
            producto = uow.session.get(Producto, producto_id)
            if not producto:  # si no lo encuentra
                raise HTTPException(  # tiramos una excepcion 404 con este detalle  v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )
            return producto  # devuelve el producto si lo encontro

    @staticmethod
    def create(producto_in: ProductoCreate):
        with UnitOfWork() as uow:
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

            uow.session.add(producto_db)  # preaparamos para guardar el registro
            # Usamos flush() en lugar de commit() para generar el ID en la DB
            # sin cerrar la transacción atómica del UnitOfWork
            uow.session.flush()
            uow.session.refresh(
                producto_db
            )  # refrescamos y obtenemos el ID autogenerado

            # a - VINCULAMOS CATEGORÍAS (relación muchos a muchos)
            categorias = uow.session.exec(  # inicia la ejecución de una consulta
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
                uow.session.add(link_cat)

            # b - VINCULAR LOS INGREDIENTES (muchos a muchos)
            # Acá empezamos con una clausula if, porque no es obligatorio
            # que nos pasaran un ID de ingrediente
            # El resto de la lógica es igual.
            if producto_in.ingrediente_ids:
                ingredientes = uow.session.exec(
                    select(Ingrediente).where(
                        Ingrediente.id.in_(producto_in.ingrediente_ids)
                    )
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
                    uow.session.add(link_ing)

            # Los registros ya estan preparados
            uow.commit()  # guardamos los registros (ahora sí, commit final de la transacción)
            uow.session.refresh(producto_db)

            return producto_db  # Devuelve el producto con las relaciones cargadas

    @staticmethod
    def update(producto_id: int, producto_in: ProductoUpdate):
        with UnitOfWork() as uow:
            # Buscamos el producto en la DB
            db_prod = uow.session.get(Producto, producto_id)
            if not db_prod:  # si no existe
                raise HTTPException(  # tiramos excepcion 404 con detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )

            # Convierte el objeto producto_in de pydantic en un diccionario Python
            # exclude_unset=True hace que el diccionario solo incluya los campos
            # que efectivamente envió el usuario. Lo guarda en prod_data.
            # Los otros clave valor (no enviados) no se incluirán.
            prod_data = producto_in.model_dump(
                exclude_unset=True,
                # excluir las liestas de ids (enteros) de el diccionario es
                # necesario porque estas no existen en la tabla producto
                # estan en la tabla intermedia
                exclude={"categoria_ids", "ingrediente_ids"},
            )

            # Actualizamos el objeto db_prod, que luego registraremos en la DB
            for key, value in prod_data.items():  # Para cada clave valor en prod_data
                setattr(
                    db_prod, key, value
                )  # en prod_cat, por key se reemplazan los values

            # a - ACTUALIZAMOS CATEGORÍAS (relación muchos a muchos)
            # Si en producto_in (datos a actualizar) recibimos ids de categoria
            if producto_in.categoria_ids is not None:
                categorias = uow.session.exec(
                    # trae de la tabla categorias toda categoria tenga
                    # su id dentro de la lista que nos pasaron para actualizar
                    select(Categoria).where(Categoria.id.in_(producto_in.categoria_ids))
                ).all()
                # si el conteo de objetos recuperados es distinto al de los ids
                # enviados, significa que algún id no existe y ...
                if len(categorias) != len(producto_in.categoria_ids):
                    raise HTTPException(  # tiramos excepcion 404 con el detalle  v v v
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Una o más categorías no existen en la BD",
                    )

                # Si pasamos el bloque if:
                # Implementamos patrón Limpiar y Reemplazar para
                # actualizar las relaciones muchos a muchos.
                uow.session.exec(
                    # borramos todos los registros de la tabla intermedia
                    #  donde el id sea igual de nuestro producto actual
                    delete(ProductoCategoria).where(
                        ProductoCategoria.producto_id == producto_id
                    )
                )

                # para cada categoría que nos pasaron para actualizar
                # usamos enumerate para tener seguimiento del indice
                for i, cat in enumerate(categorias):
                    uow.session.add(  # preparamos para agregar registros de:
                        ProductoCategoria(
                            producto_id=producto_id,  # asigna el id del producto
                            categoria_id=cat.id,  # asigna el de la categoria
                            # si la posicion es 0, se vuelve categoria principal
                            es_principal=(i == 0),
                            # este ultimo solo será True en la 1ra vuelta del bucle
                        )
                    )

            # b - ACTUALIZAMOS INGREDIENTES (relación muchos a muchos)
            if producto_in.ingrediente_ids is not None:
                # Si se pasaron ids de ingredientes para actualizar
                ingredientes = uow.session.exec(
                    # trae de la tabla ingredientes todo ingrediente tenga
                    # su id dentro de la lista que nos pasaron para actualizar
                    select(Ingrediente).where(
                        Ingrediente.id.in_(producto_in.ingrediente_ids)
                    )
                ).all()
                # si el conteo de objetos recuperados es distinto al de los ids
                # enviados, significa que algún id no existe y ...
                if len(ingredientes) != len(producto_in.ingrediente_ids):
                    raise HTTPException(  # lanzamos excepcion 404 con detalle v v v
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Uno o más ingredientes no existen en la BD",
                    )

                # Nuevamente, si pasamos el bloque if:
                # Implementamos patrón Limpiar y Reemplazar para
                # actualizar las relaciones muchos a muchos.

                uow.session.exec(
                    # borramos todos los registros de la tabla intermedia
                    #  donde el id sea igual de nuestro producto actual
                    delete(ProductoIngrediente).where(
                        ProductoIngrediente.producto_id == producto_id
                    )
                )

                # acá agregamos los ingredientes con un bucle for simple
                # porque no necesitamos designar ninguno como principal
                for ing in ingredientes:
                    # preparamos para guardar los registros en la tabla intermedia
                    uow.session.add(
                        ProductoIngrediente(
                            producto_id=producto_id, ingrediente_id=ing.id
                        )
                    )

            uow.session.add(
                db_prod
            )  # preparamos para guardar el registro en la tabla productos
            uow.commit()  # guardamos el registro
            uow.session.refresh(db_prod)  # refrescamos el registro

            return db_prod  # la funcion update devuelve le producto con detalles

    @staticmethod
    def delete(producto_id: int):
        with UnitOfWork() as uow:
            # Busca el producto x id
            producto = uow.session.get(Producto, producto_id)
            if not producto:  # si no o encuentra
                raise HTTPException(  # tira excepción 404 y el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Producto no encontrado",
                )

            uow.session.delete(producto)  # prepara para borrar
            uow.commit()  # borra
