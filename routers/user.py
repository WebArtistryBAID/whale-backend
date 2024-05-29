import os
import urllib.parse
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Annotated

import requests
from fastapi import APIRouter, Depends, HTTPException
from jose import jwt
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from data.models import User, OrderStatus
from data.schemas import UserSchemaSecure, UserStatisticsSchema
from utils import crud
from utils.dependencies import get_db, get_current_user

router = APIRouter()


@router.get("/login")
def login_redirect(redirect: str):
    # We are still within the SPA context here, so the redirect is performed by the SPA
    return {
        "target": "https://passport.seiue.com/authorize?response_type=token&client_id=" + os.environ["SEIUE_CLIENT_ID"] +
                  "&school_id=452&scope=reflection.read_basic" +
                  "&redirect_uri=" + urllib.parse.quote(os.environ["API_HOST"] + "/login/capture?redirect=" + urllib.parse.quote(redirect, safe=""), safe="")
    }


@router.get("/login/capture", response_class=HTMLResponse)
def login_capture_token(redirect: str):
    # We have been redirected back from SEIUE and is within a separate context from the SPA
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Please wait...</title>
</head>
<body>
    <script>
        if (location.hash.includes('access_token')) {
            const token = location.hash.replace('#', '')
            const match = token.match(/access_token=([^&]*)/)
            if (match && match[1]) {
                location.href = `exchange/?token=${match[1]}&redirect=""" + redirect + """`
            }
        } else {
            location.href = 'exchange/?error=error'
        }
    </script>
</body>
</html>
"""


@router.get("/login/exchange")
def login_token_redirect(redirect: str, error: str | None = None, token: str | None = None, db: Session = Depends(get_db)):
    if error is not None or token is None:
        return RedirectResponse(redirect + "?error=error", status_code=302)
    # Still in a separate context, but now we redirect back to the SPA with our custom token
    r = requests.get("https://open.seiue.com/api/v3/oauth/me",
                     headers={
                         "Authorization": f"Bearer {token}",
                         "X-School-Id": "452"
                     })
    if r.status_code != 200:
        return RedirectResponse(redirect + "?error=error", status_code=302)
    data = r.json()
    if crud.get_user(db, data["usin"]) is None:
        user = crud.create_user(db, data["usin"], data["name"], data.get("pinyin"), data.get("phone"))
    else:
        user = crud.update_user(db, crud.get_user(db, data["usin"]), data["name"], data.get("pinyin"), data.get("phone"))
    to_encode = {"name": data["name"], "id": data["usin"], "permissions": user.permissions,
            "exp": datetime.now(timezone.utc) + timedelta(days=30)}
    encoded = jwt.encode(to_encode, key=os.environ["JWT_SECRET_KEY"], algorithm="HS256")
    return RedirectResponse(redirect + "?token=" + urllib.parse.quote(encoded, safe="") + "&name=" + urllib.parse.quote(data["name"], safe=""), status_code=302)


@router.get("/login/test")
def login_test(db: Session = Depends(get_db)):
    if os.environ.get("DEVELOPMENT") != "true":
        raise HTTPException(status_code=403)
    if crud.get_user(db, "00000000") is None:
        crud.create_user(db, "00000000", "Test", "Test", "0000")
    to_encode = {"name": "Test", "id": "00000000", "exp": datetime.now(timezone.utc) + timedelta(days=30)}
    encoded = jwt.encode(to_encode, key=os.environ["JWT_SECRET_KEY"], algorithm="HS256")
    return RedirectResponse(os.environ["FRONTEND_HOST"] + "/login/onboarding/_?token=" + urllib.parse.quote(encoded, safe="") + "&name=Test", status_code=302)


@router.get("/me", response_model=UserSchemaSecure)
def me(user: Annotated[User, Depends(get_current_user)]):
    return user


@router.get("/me/statistics", response_model=UserStatisticsSchema)
def me_statistics(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user.id)
    orders_amount = len(orders)
    total_spent = Decimal(0)
    total_cups = 0
    deletable = True
    for order in orders:
        total_spent += order.totalPrice
        for item in order.items:
            total_cups += item.amount
        if order.status != OrderStatus.pickedUp:
            deletable = False
    return UserStatisticsSchema(
        totalOrders=orders_amount,
        totalSpent=total_spent,
        totalCups=total_cups,
        deletable=deletable
    )


@router.delete("/me", response_model=bool)
def delete_me(user: Annotated[User, Depends(get_current_user)], db: Session = Depends(get_db)):
    orders = crud.get_orders_by_user(db, user.id)
    for order in orders:
        if order.status != OrderStatus.pickedUp:
            raise HTTPException(status_code=403, detail='Cannot delete user with active orders')
    crud.delete_user(db, user)
    return True
