from typing import Optional, List, Text
from pydantic import BaseModel, ConfigDict


#
# Users
#
class SUsersAdd(BaseModel):
    login: str
    password: str
    first_name: str
    second_name: str
    middle_name: str
    email: str
    phone: str
    is_admin: int


class SUsers(SUsersAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SUserUpdate(BaseModel):
    password: Optional[str] = None
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    middle_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None


#
# Projects
#
class SProjectsAdd(BaseModel):
    name: str
    description: str
    tasks: Optional[List[int]] = None


class SProjects(SProjectsAdd):
    id: int
    model_config = ConfigDict(from_attributes=True)


class SProjectsUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    tasks: Optional[List[int]] = None


#
# Tasks
#
class STaskAdd(BaseModel):
    name: str
    description: str
    date_start: Optional[int] = None
    date_end: Optional[int] = None
    progress: int
    status: int
    priority: int
    created_by: int
    admin: int
    executor: int
    last_modified_time: Optional[int] = None


class STask(STaskAdd):
    id: int
    files: Optional[List[int]] = None
    model_config = ConfigDict(from_attributes=True)


class STaskUpdate(BaseModel):
    date_start: Optional[int] = None
    date_end: Optional[int] = None
    progress: Optional[int] = None
    status: Optional[int] = None
    priority: Optional[int] = None
    executor: Optional[int] = None
    related_tasks: Optional[List[int]] = None
    history: Optional[List[int]] = None


#
# HistoryElements
#
class SHistoryElementsAdd(BaseModel):
    timestamp: int
    text: Optional[Text] = None
    by_user: int
    new_date_start: Optional[int] = None
    new_date_end: Optional[int] = None
    new_progress: Optional[int] = None
    new_status: Optional[int] = None
    new_priority: Optional[int] = None
    new_executor: Optional[int] = None
    new_related_tasks: Optional[List[int]] = None


class SHistoryElements(SHistoryElementsAdd):
    id: int
    files: Optional[List[int]] = None
    model_config = ConfigDict(from_attributes=True)


class SHistoryGetByIdArray(BaseModel):
    id: List[int]


class SHistoryElementsUpdate(BaseModel):
    text: Text


class SHistoryGetUserId(BaseModel):
    id: int
