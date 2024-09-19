from contextlib import contextmanager

from fastapi_storages import FileSystemStorage
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

engine = create_engine(os.getenv("DATABASE_URL"))
storage = FileSystemStorage("uploads")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


@contextmanager
def ind_db():
    db = SessionLocal()
    try:
        yield db
    except:
        # if we fail somehow rollback the connection
        print("Failed in database operation, rolling back")
        db.rollback()
        raise
    finally:
        db.close()
