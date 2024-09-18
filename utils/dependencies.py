import os
from typing import Annotated

import pytz
from fastapi import Depends, HTTPException, Header
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from utils import crud
from data.database import SessionLocal

TIME_ZONE = pytz.timezone("Asia/Shanghai")
if "TIME_ZONE" in os.environ:
    TIME_ZONE = pytz.timezone(os.environ["TIME_ZONE"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(authorization: Annotated[str | None, Header()] = None, db: Session = Depends(get_db)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token = authorization.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        return crud.ensure_not_none(crud.get_user(db, payload["id"]))
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
