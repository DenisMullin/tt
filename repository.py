import os
import shutil
import string
import random

from typing import TypeVar, Type, Optional, Any, List

from fastapi import UploadFile
from sqlalchemy import select, ColumnElement
from sqlalchemy.ext.asyncio import AsyncSession

from database import new_session, TaskOrm, UsersOrm, HistoryElementsOrm, FilesOrm
from schemas import SUsersAdd, SUsers, SUserUpdate, SHistoryElementsUpdate, \
    SHistoryGetByIdArray, SHistoryGetUserId
from schemas import STaskAdd, STask, STaskUpdate, SHistoryElementsAdd, SHistoryElements


OrmModel = TypeVar('OrmModel')
PydanticModel = TypeVar('PydanticModel')


def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


async def get_by_id(
        session: AsyncSession,
        model_orm: Type[OrmModel],
        model_pydantic: Type[PydanticModel],
        record_id: int
) -> Optional[PydanticModel]:
    query = select(model_orm).where(model_orm.id == record_id)
    result = await session.execute(query)
    model_instance = result.scalars().first()
    if model_instance:
        return model_pydantic.model_validate(model_instance)
    return None


async def add_one(
        session: AsyncSession,
        data: PydanticModel,
        model_orm: Type[OrmModel],
) -> int:
    model_dict = data.dict()
    model_instance = model_orm(**model_dict)
    session.add(model_instance)
    await session.flush()
    await session.commit()
    return model_instance.id


async def update_one(
        session: AsyncSession,
        record_id: int,
        data: PydanticModel,
        model_orm: Type[OrmModel],
) -> bool:
    instance = await session.get(model_orm, record_id)
    if instance is None:
        return False
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in update_data.items():
        setattr(instance, key, value)
    await session.commit()
    return True


async def get_list(
        session: AsyncSession,
        data: Type[PydanticModel],
        model_orm: Type[OrmModel]
) -> list[PydanticModel]:
    query = select(model_orm)
    result = await session.execute(query)
    models = result.scalars().all()
    schemas = [data.model_validate(model) for model in models]
    return schemas


async def get_list_by_field(
        field_name: str,
        field_value: Any,
        session: AsyncSession,
        model_orm: Type[OrmModel],
        pydantic_model: Type[PydanticModel]
) -> Optional[list[PydanticModel]]:
    field: ColumnElement = getattr(model_orm, field_name)
    print(field)
    if not field:
        return None
    query = select(model_orm).where(field == field_value)
    result = await session.execute(query)
    models = result.scalars().all()
    schemas = [pydantic_model.model_validate(model) for model in models]
    return schemas


class BaseRepository:
    orm_model: Type[OrmModel]
    pydantic_model: Type[PydanticModel]
    pydantic_model_add: Type[PydanticModel]
    pydantic_model_update: Type[PydanticModel]

    @classmethod
    async def add_one(cls, data: PydanticModel) -> int:
        async with new_session() as session:
            return await add_one(session, data, cls.orm_model)

    @classmethod
    async def find_all(cls) -> list[PydanticModel]:
        async with new_session() as session:
            return await get_list(session, cls.pydantic_model, cls.orm_model)

    @classmethod
    async def update_one(cls, id: int, data: PydanticModel) -> bool:
        async with new_session() as session:
            return await update_one(session, id, data, cls.orm_model)

    @classmethod
    async def get_by_id(cls, id: int) -> Type[PydanticModel]:
        async with new_session() as session:
            return await get_by_id(session, cls.orm_model, cls.pydantic_model, id)

    @classmethod
    async def get_list_by_field(cls, field_name: str, value: Any) -> Optional[Type[PydanticModel]]:
        async with new_session() as session:
            return await get_list_by_field(field_name, value, session, cls.orm_model, cls.pydantic_model)


class TaskRepository(BaseRepository):
    orm_model = TaskOrm
    pydantic_model = STask
    pydantic_model_add: STaskAdd
    pydantic_model_update: STaskUpdate

    @classmethod
    async def update_task_files_add(cls, id: int, files: List[UploadFile]) -> bool:
        async with new_session() as session:
            task = await session.get(TaskOrm, id)
            if not task:
                return False
            uploaded_files = []
            for file in files:
                random_suffix = generate_random_string()
                sub_path = f"{random_suffix}/{file.filename}"
                file_path = f'media/{sub_path}'
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb+') as buffer:
                    shutil.copyfileobj(file.file, buffer)
                    model_instance = FilesOrm(name=file.filename, path=file_path, size=os.path.getsize(file_path))
                    session.add(model_instance)
                    await session.flush()
                    uploaded_files.append(model_instance.id)
            if task.files:
                task.files.extend(uploaded_files)
            else:
                task.files = uploaded_files
            await session.commit()

            return True



class UsersRepository(BaseRepository):
    orm_model = UsersOrm
    pydantic_model = SUsers
    pydantic_model_add: SUsersAdd
    pydantic_model_update: SUserUpdate


class HistoryRepository(BaseRepository):
    orm_model = HistoryElementsOrm
    pydantic_model = SHistoryElements
    pydantic_model_add: SHistoryElementsAdd
    pydantic_model_update: SHistoryElementsUpdate

    @classmethod
    async def find_by_id_array(cls, id_array: SHistoryGetByIdArray) -> list[SHistoryElements]:
        async with new_session() as session:
            query = select(HistoryElementsOrm).where(HistoryElementsOrm.id.in_(id_array.id))
            result = await session.execute(query)
            models = result.scalars().all()
            elements = [SHistoryElements.model_validate(model) for model in models]
            return elements

    @classmethod
    async def get_by_user_id(cls, user_id: int) -> list[SHistoryElements]:
        async with new_session() as session:
            query = select(HistoryElementsOrm).where(HistoryElementsOrm.by_user == user_id)
            result = await session.execute(query)
            models = result.scalars().all()
            elements = [SHistoryElements.model_validate(model) for model in models]
            return elements

    @classmethod
    async def update_history_files_add(cls, id: int, files: List[UploadFile]) -> bool:
        async with new_session() as session:
            history = await session.get(HistoryElementsOrm, id)
            if not history:
                return False
            uploaded_files = []
            for file in files:
                random_suffix = generate_random_string()
                sub_path = f"{random_suffix}/{file.filename}"
                file_path = f'media/{sub_path}'
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'wb+') as buffer:
                    shutil.copyfileobj(file.file, buffer)
                    model_instance = FilesOrm(name=file.filename, path=file_path, size=os.path.getsize(file_path))
                    session.add(model_instance)
                    await session.flush()
                    uploaded_files.append(model_instance.id)
            if history.files:
                history.files.extend(uploaded_files)
            else:
                history.files = uploaded_files
            await session.commit()
            return True
