from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.orm import Session

from data.models import OrderStatus, Order, User
from data.schemas import ItemTypeSchema, CategorySchema, OrderSchema, OrderEstimateSchema, OrderCreateSchema, AdSchema
from utils import crud
from utils.dependencies import get_db, get_current_user

router = APIRouter()


@router.get("/items", response_model=list[ItemTypeSchema])
def get_items(category: int | None = None, db: Session = Depends(get_db)):
    if category is not None:
        return crud.get_item_types_by_category(db, category)
    return crud.get_item_types(db)


@router.get("/item", response_model=ItemTypeSchema)
def get_item(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_item_type(db, id))


@router.get("/categories", response_model=list[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    return crud.get_categories(db)


@router.get("/category", response_model=CategorySchema)
def get_category(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_category(db, id))


@router.get("/settings", response_model=str)
def get_setting(key: str, db: Session = Depends(get_db)):
    setting = crud.get_settings(db, key)
    return "0" if setting is None else setting.value


@router.get("/order", response_model=OrderSchema)
def get_order(id: int, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_order(db, id))


@router.get("/order/bynumber", response_model=OrderSchema)
def get_order(number: str, db: Session = Depends(get_db)):
    return crud.ensure_not_none(crud.get_order_by_number(db, number))


@router.get("/order/estimate", response_model=OrderEstimateSchema)
def estimate(id: int | None = None, db: Session = Depends(get_db)):
    amount = 0
    order = None
    if id is not None:
        order = crud.ensure_not_none(crud.get_order(db, id))
        if order.status == OrderStatus.ready or order.status == OrderStatus.pickedUp:
            return OrderEstimateSchema(
                time=0,
                orders=0,
                type=None if order is None else order.type,
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
        type=None if order is None else order.type,
        number=None if order is None else order.number,
        status=None if order is None else order.status
    )


@router.delete("/order", response_model=bool)
def cancel_order(id: int, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if user.blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    order = crud.ensure_not_none(crud.get_order(db, id))
    if (order.status == OrderStatus.notStarted and order.userId == user.id) or "admin.manage" in user.permissions:
        crud.delete_order(db, order)
        return True
    raise HTTPException(status_code=401, detail="Order already started")


@router.post("/order", response_model=OrderSchema)
def order(order: OrderCreateSchema, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if user.blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    if order.onSiteOrder and "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permissions denied")
    if not order.onSiteOrder:
        for o in crud.get_orders_by_user(db, user.id):
            if o.status != OrderStatus.pickedUp:
                raise HTTPException(status_code=403, detail="User has an active order")
    return crud.create_order(db, order, user)


@router.get("/orders", response_model=Page[OrderSchema])
def user_orders(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if user.blocked:
        raise HTTPException(status_code=403, detail="User is blocked")
    return paginate(db, crud.get_orders_query_by_user(user.id))


@router.get("/pms", response_model=list[AdSchema])
def ads(db: Session = Depends(get_db)):
    return crud.get_ads(db)
