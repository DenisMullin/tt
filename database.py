from typing import Optional

from sqlalchemy import Integer, String, JSON, Text, Table
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

engine = create_async_engine("postgresql+asyncpg://postgres:1234@127.0.0.1:5416/tt")
new_session = async_sessionmaker(engine, expire_on_commit=False)


class Model(DeclarativeBase):
    pass


class UsersOrm(Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(String)
    password: Mapped[str] = mapped_column(String)
    first_name: Mapped[str] = mapped_column(String)
    second_name: Mapped[str] = mapped_column(String)
    middle_name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String)
    phone: Mapped[str] = mapped_column(String)
    is_admin: Mapped[int] = mapped_column(Integer, default=0)
    fav_tasks: Mapped[Optional[JSON]] = mapped_column(type_=JSON, nullable=True)


class ProjectsOrm(Model):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    tasks: Mapped[Optional[JSON]] = mapped_column(type_=JSON)


class TaskOrm(Model):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str]
    description: Mapped[Text] = mapped_column(Text)
    date_start: Mapped[Optional[int]] = mapped_column(Integer)
    date_end: Mapped[Optional[int]] = mapped_column(Integer)
    progress: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    status: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    priority: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    created_by: Mapped[int] = mapped_column(Integer)
    admin: Mapped[int] = mapped_column(Integer)
    executor: Mapped[int] = mapped_column(Integer)
    last_modified_time: Mapped[Optional[int]] = mapped_column(Integer)
    history: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    related_tasks: Mapped[Optional[JSON]] = mapped_column(type_=JSON)
    files: Mapped[Optional[JSON]] = mapped_column(type_=JSON, nullable=True)


class HistoryElementsOrm(Model):
    __tablename__ = "history_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    timestamp: Mapped[int] = mapped_column(Integer)
    text: Mapped[Text] = mapped_column(Text)
    by_user: Mapped[int] = mapped_column(Integer)
    new_date_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_date_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_progress: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    new_status: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    new_priority: Mapped[Optional[int]] = mapped_column(Integer, default=1)
    new_executor: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_related_tasks: Mapped[Optional[JSON]] = mapped_column(type_=JSON, nullable=True)
    files: Mapped[Optional[JSON]] = mapped_column(type_=JSON, nullable=True)


class FilesOrm(Model):
    __tablename__ = 'files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    path: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)


async def create_tables():
    # https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-core
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.create_all)


async def delete_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Model.metadata.drop_all)
