from fastapi import HTTPException, status
from sqlmodel import select
from app.uow.unit_of_work import UnitOfWork
from app.models.catalog import Categoria
from app.schemas.catalog import CategoriaCreate, CategoriaUpdate


class CategoriaService:
    @staticmethod
    def get_all(offset: int, limit: int):
        with UnitOfWork() as uow:
            # consulta SQL con SQLModel, aplica filtros de paginación, trae rodos los resultados.
            categorias = uow.session.exec(
                select(Categoria).offset(offset).limit(limit)
            ).all()
            return categorias

    @staticmethod
    def get_by_id(categoria_id: int):
        with UnitOfWork() as uow:
            # Buscamos el producto desde la DB con el ID
            categoria = uow.session.get(Categoria, categoria_id)
            if not categoria:  # si no existe
                raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )
            return categoria  # devolvemos la categoría

    @staticmethod
    def create(categoria_in: CategoriaCreate):
        with UnitOfWork() as uow:
            # Pydantic transforma el objeto categoria_in (de forma CategoriaCreate)
            # en un diccionario estadar de python usando .model_dump()
            # Los "**" hacen el desempaquetado de los pares clave valor
            # a argumentos para armar un objeto del modelo Categoria y guardarlo
            # categoria_db.
            categoria_db = Categoria(**categoria_in.model_dump())
            uow.session.add(categoria_db)  # prepara para guardar el registro
            uow.commit()  # guarda el registro
            uow.session.refresh(
                categoria_db
            )  # actualiza el objeto para mostrar el id autogenerado
            return categoria_db  # devuelve el objeto cread

    @staticmethod
    def update(categoria_id: int, categoria_in: CategoriaUpdate):
        with UnitOfWork() as uow:
            # Buscamos la categoria en la DB
            db_cat = uow.session.get(Categoria, categoria_id)
            if not db_cat:  # si no la encontramos
                raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )

            # Convierte el objeto categoria_in de pydantic en un diccionario de Python
            # exclude_unset=True hace que el diccionario solo incluya los campos
            # que efectivamente envió el usuario. Lo guarda en cat_data.
            # Los otros clave valor (no enviados) no se incluirán.
            cat_data = categoria_in.model_dump(exclude_unset=True)

            for key, value in cat_data.items():  # Para cada clave valor en cat_data
                setattr(
                    db_cat, key, value
                )  # en db_cat, por key se reemplazan los values

            uow.session.add(db_cat)  # preparamos para guardar registo
            uow.commit()  # guarda el registro
            uow.session.refresh(db_cat)  # refresca el registro
            return db_cat  # devuelve el registro

    @staticmethod
    def delete(categoria_id: int):
        with UnitOfWork() as uow:
            # Buscamos el registro en la DB
            categoria = uow.session.get(Categoria, categoria_id)
            if not categoria:  # si no lo encontramos
                raise HTTPException(  # lanzamos excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Categoría no encontrada",
                )

            uow.session.delete(categoria)  # prepara para borrar
            uow.commit()  # borra
