from fastapi import HTTPException, status
from sqlmodel import select
from app.uow.unit_of_work import UnitOfWork
from app.models.catalog import Ingrediente
from app.schemas.catalog import IngredienteCreate, IngredienteUpdate


class IngredienteService:
    @staticmethod
    def get_all(offset: int, limit: int):
        with UnitOfWork() as uow:
            # consulta SQL con SQLModel, aplica filtros de paginación, trae todos los resultados.
            ingredientes = uow.session.exec(
                select(Ingrediente).offset(offset).limit(limit)
            ).all()
            return ingredientes

    @staticmethod
    def get_by_id(ingrediente_id: int):
        with UnitOfWork() as uow:
            # Buscamos el ingrediente desde la DB con el ID
            ingrediente = uow.session.get(Ingrediente, ingrediente_id)
            if not ingrediente:  # si no existe
                raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ingrediente no encontrado",
                )
            return ingrediente  # devolvemos el ingrediente

    @staticmethod
    def create(ingrediente_in: IngredienteCreate):
        with UnitOfWork() as uow:
            # Validación de duplicados por nombre
            existente = uow.session.exec(
                select(Ingrediente).where(Ingrediente.nombre == ingrediente_in.nombre)
            ).first()
            if existente:  # si ya hay un ingrediente con ese nombre
                raise HTTPException(  # lanzamos excepción 400
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El nombre del ingrediente ya existe",
                )

            # Pydantic transforma el objeto ingrediente_in en un diccionario
            # de python usando .model_dump(). Los "**" desempaquetan los datos.
            ingrediente_db = Ingrediente(**ingrediente_in.model_dump())
            uow.session.add(ingrediente_db)  # prepara para guardar el registro
            uow.commit()  # guarda el registro
            uow.session.refresh(
                ingrediente_db
            )  # actualiza el objeto para mostrar el id autogenerado
            return ingrediente_db  # devuelve el objeto creado

    @staticmethod
    def update(ingrediente_id: int, ingrediente_in: IngredienteUpdate):
        with UnitOfWork() as uow:
            # Buscamos el ingrediente en la DB
            db_ing = uow.session.get(Ingrediente, ingrediente_id)
            if not db_ing:  # si no lo encontramos
                raise HTTPException(  # lanzamos una excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ingrediente no encontrado",
                )

            # Convierte el objeto ingrediente_in de pydantic en un diccionario de Python
            # exclude_unset=True hace que el diccionario solo incluya los campos
            # que efectivamente envió el usuario.
            ing_data = ingrediente_in.model_dump(exclude_unset=True)

            for key, value in ing_data.items():  # Para cada clave valor enviada
                setattr(
                    db_ing, key, value
                )  # actualizamos los atributos en el objeto recuperado

            uow.session.add(db_ing)  # preparamos para guardar registro
            uow.commit()  # guarda el registro
            uow.session.refresh(db_ing)  # refresca el registro
            return db_ing  # devuelve el registro actualizado

    @staticmethod
    def delete(ingrediente_id: int):
        with UnitOfWork() as uow:
            # Buscamos el registro en la DB
            ingrediente = uow.session.get(Ingrediente, ingrediente_id)
            if not ingrediente:  # si no lo encontramos
                raise HTTPException(  # lanzamos excepción 404 con el detalle v v v
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ingrediente no encontrado",
                )

            uow.session.delete(ingrediente)  # prepara para borrar
            uow.commit()  # borra
