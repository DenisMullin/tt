from typing import Annotated, Optional, Any, List

from fastapi import APIRouter, Depends, UploadFile, File

from repository import TaskRepository, HistoryRepository
from repository import UsersRepository
from schemas import STaskAdd, STask, STaskUpdate, SHistoryGetByIdArray, SHistoryGetUserId, SUserUpdate
from schemas import SUsersAdd, SUsers
from schemas import SHistoryElementsAdd, SHistoryElements, SHistoryElementsUpdate

router_tasks = APIRouter(
    prefix="/api/tasks",
    tags=["Задачи"],
)

router_users = APIRouter(
    prefix='/api/users',
    tags=["Пользователь"]
)

router_history = APIRouter(
    prefix='/api/history',
    tags=["История изменений задач"]
)


#
#   Tasks
#
@router_tasks.post("/add")
async def add_task(
        task: Annotated[STaskAdd, Depends()],
) -> int:
    return await TaskRepository.add_one(task)


@router_tasks.get("/get")
async def get_tasks() -> list[STask]:
    return await TaskRepository.find_all()


@router_tasks.post("/update")
async def update_task(
        task_id: int,
        fields: Annotated[STaskUpdate, Depends()],
) -> bool:
    return await TaskRepository.update_one(task_id, fields)


@router_tasks.post('/update_files')
async def update_task_files_add(
        task_id: int,
        files: List[UploadFile] = File(...),
) -> bool:
    return await TaskRepository.update_task_files_add(task_id, files)


@router_tasks.post("/get_one")
async def get_one_task(
        task_id: int,
) -> bool:
    return await TaskRepository.get_by_id(task_id)


#
#   Users
#
@router_users.post("/add")
async def add_user(
        user: Annotated[SUsersAdd, Depends()],
) -> int:
    return await UsersRepository.add_one(user)


@router_users.post("/update")
async def update_user(
        user_id: int,
        user: Annotated[SUserUpdate, Depends()],
) -> bool:
    return await UsersRepository.update_one(user_id, user)


@router_users.get("/get")
async def get_users() -> list[SUsers]:
    return await UsersRepository.find_all()


@router_users.get("/get_one")
async def get_user_by_id(
        user_id: int
) -> SUsers:
    return await UsersRepository.get_by_id(user_id)


#
#   History
#
@router_history.post('/add')
async def add_history(
        fields: Annotated[SHistoryElementsAdd, Depends()],
) -> int:
    return await HistoryRepository.add_one(fields)


@router_history.get('/get')
async def get_history() -> list[SHistoryElements]:
    return await HistoryRepository.find_all()


@router_history.post('/update')
async def update_history(
        id: int,
        fields: Annotated[SHistoryElementsUpdate, Depends()],
) -> bool:
    return await HistoryRepository.update_one(id, fields)


@router_history.get('/get_by_id_array')
async def find_by_id_array(
    id_array: Annotated[SHistoryGetByIdArray, Depends()],
) -> list[SHistoryElements]:
    return await HistoryRepository.find_by_id_array(id_array)


@router_history.get('/get_by_user_id')
async def get_by_user_id(
        user_id: int,
) -> list[SHistoryElements]:
    return await HistoryRepository.get_by_user_id(user_id)


@router_history.post('/get_by_user_id_test')
async def get_by_user_id_test(
        field_name: str,
        value: int
) -> Optional[list[SHistoryElements]]:
    return await HistoryRepository.get_list_by_field(field_name, value)


@router_history.post('/update_files')
async def update_history_files_add(
        id: int,
        files: List[UploadFile] = File(...),
) -> bool:
    return await HistoryRepository.update_history_files_add(id, files)
