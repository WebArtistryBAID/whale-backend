from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

import crud
from database import SessionLocal
from models import Order, OrderStatus
from schemas import *

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    if id is not None:
        order = crud.ensure_not_none(crud.get_order(db, id))
        if order.status == OrderStatus.ready or order.status == OrderStatus.pickedUp:
            raise HTTPException(status_code=401, detail="Already finished")
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
        orders=len(matching_orders)
    )


@app.delete("/order", response_model=bool)
def cancel_order(id: int, db: Session = Depends(get_db)):
    order = crud.ensure_not_none(crud.get_order(db, id))
    if order.status == OrderStatus.notStarted:
        crud.delete_order(db, order)
        return True
    raise HTTPException(status_code=401, detail="Order already started")


@app.post("/order", response_model=OrderSchema)
def order(order: OrderCreateSchema, db: Session = Depends(get_db)):
    return crud.create_order(db, order)
