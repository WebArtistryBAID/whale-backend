import os
import urllib.parse
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from data.admin import create_admin
from data.database import engine
from routers import user, api, manage
from utils.scheduling import start_scheduler

app = FastAPI(root_path=urllib.parse.urlparse(os.environ['API_HOST']).path)

if os.environ.get("DEVELOPMENT") == "true":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if not os.path.exists("uploads"):
    os.makedirs("uploads")

scheduler = start_scheduler()


@asynccontextmanager
async def lifespan(app):
    try:
        yield
    finally:
        scheduler.shutdown()


app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(api.router)
app.include_router(manage.router)
app.include_router(user.router)
create_admin(app, engine)


@app.middleware("http")
async def fix_admin_root_path(request, call_next):
    if request.url.path.startswith("/admin/"):
        request.scope["path"] = app.root_path + request.url.path
    return await call_next(request)


add_pagination(app)
