from datetime import timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException
from jose import JWTError, jwt
import os
import re
import requests
from sqlalchemy.orm import Session

import crud
from database import SessionLocal
from models import Order, OrderStatus, User
from schemas import *

app = FastAPI()


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


@app.get("/token", response_model=AccessToken)
def login(username: str, password: str, db: Session = Depends(get_db)):
    r = requests.post("https://passport.seiue.com/login?school_id=452",
                  data={"email": username, "password": password, "school_id": "452", "submit": "Submit"},
                  headers={"Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Mozilla/5.0 (Wayland; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"})
    result = r.text.replace(" ", "").replace("\n", "").strip()
    matches_name = re.findall(r',"name":"([^"]+)","old_user_id":null,"outer_id":null,', result)
    matches_id = re.findall(r'"usin":"(\d+)"', result)
    
    if len(matches_name) < 1 or len(matches_id) < 1:
        raise HTTPException(status_code=401, detail="Login failed")
    data = {"name": matches_name[0].encode().decode("unicode-escape"), "id": matches_id[0], "exp": datetime.now(timezone.utc) + timedelta(days=30)}
    if crud.get_user(db, data["id"]) is None:
        crud.create_user(db, data["id"], data["name"])
    encoded = jwt.encode(data, os.environ["JWT_SECRET_KEY"], algorithm="HS256")
    return AccessToken(access_token=encoded, token_type="Bearer")


@app.get("/items", response_model=list[ItemTypeSchema])
def get_items(category: int | None = None, db: Session = Depends(get_db)):
    if category is not None:
        return crud.get_item_types_by_category(db, category)
    return crud.get_item_types(db)


@app.get("/item", response_model=ItemTypeSchema)
def get_item(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_item_type(db, id))


@app.get("/categories", response_model=list[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@app.get("/category", response_model=CategorySchema)
def get_category(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_category(db, id))


@app.get("/settings", response_model=str)
def get_setting(key: str, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_settings(db, key)).value


@app.get("/order", response_model=OrderSchema)
def get_order(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_order(db, id))


@app.get("/order/bynumber", response_model=OrderSchema)
def get_order(number: str, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_order_by_number(db, number))


@app.get("/order/estimate", response_model=OrderEstimateSchema)
def estimate(id: int | None = None, db: Session = Depends(get_db)):
    amount = 0
    order = None
    if id is not None:
        order = crud.ensure_not_none(crud.get_order(db, id))
        if order.status == OrderStatus.ready or order.status == OrderStatus.pickedUp:
            return OrderEstimateSchema(
                time=0,
                orders=0,
                number=None if order is None else order.number,
                status=None if order is None else order.status
            )
        for item in order.items:
            amount += item.amount
        matching_orders = (db.query(Order)
                           .filter(Order.createdTime < order.createdTime)
                           .filter(Order.status.in_([OrderStatus.notStarted, OrderStatus.inProgress]))
                           .all())
    else:
        matching_orders = (db.query(Order)
                           .filter(Order.status.in_([OrderStatus.notStarted, OrderStatus.inProgress]))
                           .all())

    for o in matching_orders:
        for i in o.items:
            amount += i.amount
    return OrderEstimateSchema(
        time=amount * 2,
        orders=len(matching_orders),
        number=None if order is None else order.number,
        status=None if order is None else order.status
    )


@app.delete("/order", response_model=bool)
def cancel_order(id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    order = crud.ensure_not_none(crud.get_order(db, id))
    if order.status == OrderStatus.notStarted and order.userId == user.id:
        crud.delete_order(db, order)
        return True
    raise HTTPException(status_code=401, detail="Order already started")


@app.post("/order", response_model=OrderSchema)
def order(order: OrderCreateSchema, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_order(db, order, user)
