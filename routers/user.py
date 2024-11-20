import base64
import os
import urllib.parse
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from starlette.responses import RedirectResponse

from data.models import User, OrderStatus
from data.schemas import UserSchemaSecure, UserStatisticsSchema, MeCanOrderResultSchema
from utils import crud
from utils.dependencies import get_db, get_current_user

router = APIRouter()


@router.get("/login/authorize")
def login_authorize(code: str | None = None, error: str | None = None, db: Session = Depends(get_db)):
    if error == "access_denied":
        return RedirectResponse(os.environ["FRONTEND_HOST"], status_code=302)
    if code is None:
        return RedirectResponse(os.environ["FRONTEND_HOST"] + "/login/onboarding?error=error", status_code=302)

    # Exchange data
    r = requests.post(os.environ["ONELOGIN_HOST"] + "/oauth2/token", {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": os.environ["API_HOST"] + "/login/authorize"
    }, headers={
        "Authorization": "Basic " + base64.b64encode((os.environ["ONELOGIN_CLIENT_ID"] + ":" + os.environ["ONELOGIN_CLIENT_SECRET"]).encode("utf-8")).decode("utf-8")
    })

    data = r.json()
    if "error" in data:
        return RedirectResponse(os.environ["FRONTEND_HOST"] + "/login/onboarding?error=error", status_code=302)
    access_token = data["access_token"]

    r = requests.get(os.environ["ONELOGIN_HOST"] + "/api/v1/me",
                     headers={"Authorization": "Bearer " + access_token})
    data = r.json()

    if crud.get_user(db, data["schoolId"]) is None:
        user = crud.create_user(db, data["schoolId"], data["name"], data["pinyin"], data.get("phone"))
    else:
        user = crud.update_user(db, crud.get_user(db, data["schoolId"]), data["name"], data.get("pinyin"), data.get("phone"))
    to_encode = {"name": data["name"], "id": data["schoolId"], "permissions": user.permissions,
                 "exp": datetime.now(timezone.utc) + timedelta(days=30)}
    encoded = jwt.encode(to_encode, key=os.environ["JWT_SECRET_KEY"], algorithm="HS256")

    response = RedirectResponse(os.environ["FRONTEND_HOST"] + "/login/onboarding?token=" + urllib.parse.quote(encoded, safe="") + "&name=" + urllib.parse.quote(data["name"], safe=""), status_code=302)
    response.set_cookie("token", encoded, httponly=True, expires=datetime.now(timezone.utc) + timedelta(days=30))
    return response


@router.get("/me", response_model=UserSchemaSecure)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.get("/me/can-order", response_model=MeCanOrderResultSchema)
def me_can_order(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    for o in crud.get_orders_by_user(db, user.id):
        if o.status != OrderStatus.done or not o.paid:
            return MeCanOrderResultSchema(
                result=False,
                orderId=o.id,
                orderNumber=o.number,
                orderTotalPrice=o.totalPrice,
                orderDate=o.createdTime
            )
    return MeCanOrderResultSchema(
        result=True,
        orderId=None,
        orderNumber=None,
        orderTotalPrice=None,
        orderDate=None
    )


@router.get("/me/statistics", response_model=UserStatisticsSchema)
def me_statistics(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if user.blocked:
        raise HTTPException(status_code=403, detail='User is blocked')
    orders = crud.get_orders_by_user(db, user.id)
    orders_amount = len(orders)
    total_spent = Decimal(0)
    total_cups = 0
    deletable = True
    for order in orders:
        total_spent += order.totalPrice
        for item in order.items:
            total_cups += item.amount
        if order.status != OrderStatus.done or not order.paid:
            deletable = False
    return UserStatisticsSchema(
        totalOrders=orders_amount,
        totalSpent=total_spent,
        totalCups=total_cups,
        deletable=deletable
    )


@router.delete("/me", response_model=bool)
def delete_me(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    if user.blocked:
        raise HTTPException(status_code=403, detail='Cannot delete blocked user')
    orders = crud.get_orders_by_user(db, user.id)
    for order in orders:
        if order.status != OrderStatus.done or not order.paid:
            raise HTTPException(status_code=403, detail='Cannot delete user with active orders')
    crud.delete_user(db, user)
    return True
