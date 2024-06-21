from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from database import create_tables, delete_tables
from router import router_tasks, router_users, router_history

@asynccontextmanager
async def lifespan(app: FastAPI):
    await delete_tables()
    print("База очищена")
    await create_tables()
    print("База готова к работе")
    yield
    print("Выключение")


# app = FastAPI(lifespan=lifespan)
app = FastAPI()
app.include_router(router_tasks)
app.include_router(router_users)
app.include_router(router_history)

app.mount('/media', StaticFiles(directory='media'), name='media')
