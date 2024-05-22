import time
from datetime import timedelta, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from data.models import User, Order
from data.schemas import OrderSchema, OrderStatusUpdateSchema, StatsAggregateSchema
from utils import crud
from utils.dependencies import get_current_user, get_db

router = APIRouter()


@router.get("/orders/available", response_model=list[OrderSchema])
def available_orders(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.get_available_orders(db)


@router.patch("/order", response_model=OrderSchema)
def update_order_status(data: OrderStatusUpdateSchema, user: Annotated[User, Depends(get_current_user)],
                        db: Session = Depends(get_db)):
    order = crud.ensure_not_none(crud.get_order(db, data.id))
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    crud.update_order_status(db, order, data.status)
    return order


stats_last_cached = {"day": 0, "week": 0, "year": 0}
stats_cache = {"day": None, "week": None, "month": None}


@router.get("/statistics", response_model=StatsAggregateSchema)
def statistics(by: str, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    global stats_last_cached, stats_cache
    if "admin.statistics" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    if time.time() - stats_last_cached[by] < 1200 and stats_cache[by] is not None:
        return stats_cache[by]

    def get_start_of_week(date):
        return date - timedelta(days=date.weekday())

    def get_start_of_month(date):
        return datetime(date.year, date.month, 1)

    if by == "week":
        get_start_date = get_start_of_week
    elif by == "month":
        get_start_date = get_start_of_month
    else:  # Default to by day
        get_start_date = lambda x: x

    orders = db.query(Order).filter(Order.createdTime >= (datetime.now() - timedelta(days=180))).order_by(
        Order.createdTime.desc()).all()
    revenue = {}
    orders_count = {}
    unique_users = {}
    cups = {}
    for order in orders:
        day = get_start_date(order.createdTime).strftime("%Y-%m-%d")
        if day in revenue:
            revenue[day] += order.totalPrice
        else:
            revenue[day] = Decimal(order.totalPrice)

        if day in orders_count:
            orders_count[day] += 1
        else:
            orders_count[day] = 1

        cup = 0
        for item in order.items:
            cup += item.amount
        if day in cups:
            cups[day] += cup
        else:
            cups[day] = cup

        if day not in unique_users:
            unique_users[day] = set()
        unique_users[day].add(order.userId)

    for day, users in unique_users.items():
        unique_users[day] = len(users)

    stats_last_cached[by] = time.time()
    stats_cache[by] = StatsAggregateSchema(
        revenue=revenue,
        orders=orders_count,
        cups=cups,
        uniqueUsers=unique_users
    )
    return stats_cache[by]
