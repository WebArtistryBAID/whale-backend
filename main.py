import os

from fastapi import FastAPI
from fastapi_pagination import add_pagination
from starlette.middleware.cors import CORSMiddleware

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

app.include_router(api.router)
app.include_router(manage.router)
app.include_router(user.router)

add_pagination(app)
