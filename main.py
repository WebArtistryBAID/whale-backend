from fastapi import FastAPI

from routers import login, api

app = FastAPI()
app.include_router(api.router)
app.include_router(login.router)
