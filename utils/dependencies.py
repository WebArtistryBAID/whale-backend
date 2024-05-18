import os

from fastapi import Depends, HTTPException
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from utils import crud
from data.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        return crud.ensure_not_none(crud.get_user(db, payload["id"]))
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")
