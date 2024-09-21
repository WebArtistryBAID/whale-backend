import os
import time
from datetime import date, timedelta, datetime, timezone
from decimal import Decimal
from io import BytesIO
from typing import Annotated

import xlsxwriter
from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import paginate
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette.responses import Response

from data.models import User, Order, OrderType, OrderStatus
from data.schemas import OrderSchema, OrderStatusUpdateSchema, StatsAggregateSchema
from utils import crud
from utils.dependencies import get_current_user, get_db, TIME_ZONE

router = APIRouter()


@router.get("/settings/update", response_model=str)
def update_settings(key: str, value: str, user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.update_settings(db, key, value)


@router.get("/orders/today", response_model=list[OrderSchema])
def today_orders(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return crud.get_orders_today(db)


@router.get("/orders")
def all_orders(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return paginate(crud.get_orders(db))


@router.patch("/order", response_model=OrderSchema)
def update_order_status(data: OrderStatusUpdateSchema, user: Annotated[User, Depends(get_current_user)],
                        db: Session = Depends(get_db)):
    order = crud.ensure_not_none(crud.get_order(db, data.id))
    if "admin.manage" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    crud.update_order_status(db, order, data.status, data.paid)
    return order


stats_last_cached = {"day": 0, "week": 0, "month": 0, "year": 0, "individual": 0}
stats_cache = {"day": None, "week": None, "month": None, "individual": None}
stats_last_limit = 0


def get_statistics(by: str, limit: int, db: Session) -> StatsAggregateSchema:
    global stats_last_cached, stats_cache, stats_last_limit
    if time.time() - stats_last_cached[by] < 1200 and stats_cache[by] is not None and stats_last_limit == limit:
        return stats_cache[by]
    stats_last_limit = limit

    def get_start_of_week(date):
        return date - timedelta(days=date.weekday())

    def get_start_of_month(date):
        return datetime(date.year, date.month, 1, 0, 0, 0, tzinfo=TIME_ZONE)

    if by == "week":
        get_start_date = get_start_of_week
    elif by == "month":
        get_start_date = get_start_of_month
    else:  # Default to by day
        get_start_date = lambda x: x

    orders = db.query(Order).filter(Order.createdTime >= (datetime.now(tz=TIME_ZONE) - timedelta(days=limit))).order_by(
        Order.createdTime.desc()).all()
    revenue = {}
    orders_count = {}
    unique_users = {}
    cups = {}
    for order in orders:
        if by == "individual":
            day = order.createdTime.strftime("%Y-%m-%d %H:%M:%S")
        else:
            day = get_start_date(order.createdTime).strftime("%Y-%m-%d")

        if order.paid:
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

    today = date.today()

    start_of_day = datetime.combine(date.today(), datetime.min.time(), tzinfo=TIME_ZONE)
    end_of_day = datetime.combine(date.today(), datetime.max.time(), tzinfo=TIME_ZONE)
    start_of_week = get_start_of_week(today)
    end_of_week = start_of_week + timedelta(days=6)

    today_revenue = 0
    today_orders = 0
    today_cups = 0
    today_unique_users = set()
    week_revenue = 0

    for order in db.query(Order).filter(Order.createdTime >= start_of_day, Order.createdTime <= end_of_day).all():
        if order.paid:
            today_revenue += order.totalPrice
        today_orders += 1
        for item in order.items:
            today_cups += item.amount
        today_unique_users.add(order.userId)

    for order in db.query(Order).filter(Order.createdTime >= start_of_week, Order.createdTime <= end_of_week).all():
        week_revenue += order.totalPrice

    stats_last_cached[by] = time.time()
    stats_cache[by] = StatsAggregateSchema(
        todayRevenue=today_revenue,
        todayOrders=today_orders,
        todayCups=today_cups,
        todayUniqueUsers=len(today_unique_users),
        weekRevenue=week_revenue,
        weekRevenueRange=f"{start_of_week.strftime('%Y-%m-%d')} - {end_of_week.strftime('%Y-%m-%d')}",
        revenue=revenue,
        orders=orders_count,
        cups=cups,
        uniqueUsers=unique_users
    )
    return stats_cache[by]


@router.get("/statistics/export/token", response_model=str)
def statistics_export_token(type: str, by: str, limit: int, user: Annotated[User, Depends(get_current_user)]):
    if "admin.cms" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return jwt.encode({"type": type, "by": by, "limit": limit, "exp": datetime.now(timezone.utc) + timedelta(minutes=15)}, key=os.environ["JWT_SECRET_KEY"], algorithm="HS256")


@router.get("/statistics/export")
def statistics_export(token: str, db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, os.environ["JWT_SECRET_KEY"], algorithms=["HS256"])
        type = payload["type"]
        by = payload["by"]
        limit = payload["limit"]
    except JWTError | KeyError:
        raise HTTPException(status_code=403, detail="Invalid export token")

    if type == "statsExport":
        return export_statistics(by, limit, db)
    elif type == "ordersExport":
        return export_orders(limit, db)
    raise HTTPException(status_code=401, detail="Bad export type")


def export_orders(limit: int, db: Session):
    orders = db.query(Order).filter(Order.createdTime >= (datetime.now(tz=TIME_ZONE) - timedelta(days=limit))).order_by(
        Order.createdTime.desc()).all()

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)
    ws = workbook.add_worksheet("Orders")
    ws.write(0, 0, "ID")
    ws.write(0, 1, "Created Time")
    ws.write(0, 2, "Total Price")
    ws.write(0, 3, "User ID")
    ws.write(0, 4, "User Name")
    ws.write(0, 5, "Status")
    ws.write(0, 6, "Type")
    ws.write(0, 7, "Delivery Room")
    ws.write(0, 8, "Items")
    ws.write(0, 9, "On-Site Name")
    ws.write(0, 10, "Paid")

    row = 1
    for order in orders:
        ws.write(row, 0, order.id)
        ws.write(row, 1, order.createdTime.strftime("%Y-%m-%d %H:%M:%S"))
        ws.write(row, 2, str(order.totalPrice))
        ws.write(row, 3, order.userId if order.userId is not None else "On-Site Ordering")
        ws.write(row, 4, order.user.name if order.userId is not None else "On-Site Ordering")
        ws.write(row, 5, {
            OrderStatus.waiting: "Waiting",
            OrderStatus.done: "Done"
        }[order.status])
        ws.write(row, 6, {
            OrderType.pickUp: "Pick Up",
            OrderType.delivery: "Delivery"
        }[order.type])
        ws.write(row, 7, order.deliveryRoom if order.type == OrderType.delivery else "N/A")
        items = []
        for item in order.items:
            options = []
            for option in item.appliedOptions:
                options.append(option.type.name + ": " + option.name)
            items.append(f"{item.amount}x {item.itemType.name} ({', '.join(options)})")
        ws.write(row, 8, "\n".join(items))
        ws.write(row, 9, order.onSiteName if order.onSiteName is not None else "N/A")
        ws.write(row, 10, "Yes" if order.paid else "No")
        row += 1
    workbook.close()
    return Response(
        output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "inline; filename=\"exported-orders.xlsx\""
        }
    )


def export_statistics(by: str, limit: int, db: Session):
    stats = get_statistics(by, limit, db)

    output = BytesIO()
    workbook = xlsxwriter.Workbook(output)

    revenue = workbook.add_worksheet("Total Revenue")
    orders = workbook.add_worksheet("Orders")
    cups = workbook.add_worksheet("Cups")
    unique_users = workbook.add_worksheet("Unique Users")

    row = 1
    revenue.write(0, 0, "Total Revenue (From start of each time interval)")
    for ts, r in stats.revenue.items():
        revenue.write(row, 0, ts)
        revenue.write(row, 1, str(r))
        row += 1

    row = 1
    orders.write(0, 0, "Orders (From start of each time interval)")
    for ts, o in stats.orders.items():
        orders.write(row, 0, ts)
        orders.write(row, 1, str(o))
        row += 1

    row = 1
    cups.write(0, 0, "Cups (From start of each time interval)")
    for ts, c in stats.cups.items():
        cups.write(row, 0, ts)
        cups.write(row, 1, str(c))
        row += 1

    row = 1
    unique_users.write(0, 0, "Unique Users (From start of each time interval)")
    for ts, u in stats.uniqueUsers.items():
        unique_users.write(row, 0, ts)
        unique_users.write(row, 1, str(u))
        row += 1

    workbook.close()
    return Response(
        output.getvalue(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": "inline; filename=\"exported-stats.xlsx\""
        }
    )


@router.get("/statistics", response_model=StatsAggregateSchema)
def statistics(by: str, user: Annotated[User, Depends(get_current_user)], limit: int = 90, db: Session = Depends(get_db)):
    if "admin.cms" not in user.permissions:
        raise HTTPException(status_code=403, detail="Permission denied")
    return get_statistics(by, limit, db)
