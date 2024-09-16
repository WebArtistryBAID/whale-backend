import os

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles

from data.admin import create_admin
from data.database import engine
from routers import user, api, manage

app = FastAPI()

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

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(api.router)
app.include_router(manage.router)
app.include_router(user.router)
create_admin(app, engine)

add_pagination(app)
