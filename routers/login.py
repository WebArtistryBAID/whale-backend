import os
import urllib.parse
from datetime import datetime, timezone, timedelta

import requests
from fastapi import APIRouter, Depends
from jose import jwt
from sqlalchemy.orm import Session
from starlette.responses import HTMLResponse, RedirectResponse

from utils import crud
from utils.dependencies import get_db

router = APIRouter()


@router.get("/login")
def login_redirect(redirect: str):
    # We are still within the SPA context here, so the redirect is performed by the SPA
    return {
        "target": f"https://passport.seiue.com/authorize?response_type=token&client_id={os.environ["SEIUE_CLIENT_ID"]}"
                  f"&school_id=452&scope=reflection.read_basic"
                  f"&redirect_uri=({urllib.parse.quote(os.environ["API_HOST"] + f"/login/capture?redirect={urllib.parse.quote(redirect, safe="")}", safe="")}"
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
        if (location.hash.length < 1) {
            location.href = 'exchange/?error=error'
        }

        if (location.hash.includes('#access_token=')) {
            const token = location.hash.replace('#access_token=', '')
            location.href = `exchange/?token=${token}&redirect=""" + redirect + """`
        }
    </script>
</body>
</html>
"""


@router.get("/login/exchange")
def login_token_redirect(error: str | None, token: str | None, redirect: str, db: Session = Depends(get_db)):
    if error is not None or token is None:
        return RedirectResponse(redirect + "/?error=error", status_code=302)
    # Still in a separate context, but now we redirect back to the SPA with our custom token
    r = requests.get("https://open.seiue.com/api/v3/oauth/me",
                     headers={
                         "Authorization": f"Bearer {token}",
                         "X-School-Id": "452"
                     })
    if r.status_code != 200:
        return RedirectResponse(redirect + "/?error=error", status_code=302)
    data = r.json()
    if crud.get_user(db, data["usin"]) is None:
        crud.create_user(db, data["usin"], data["name"], data.get("pinyin"), data.get("phone"))
    data = {"name": data["name"], "id": data["usin"],
            "exp": datetime.now(timezone.utc) + timedelta(days=30)}
    encoded = jwt.encode(data, key=os.environ["JWT_SECRET"], algorithm="HS256")
    return RedirectResponse(redirect + "/?token=" + urllib.parse.quote(encoded, safe=""), status_code=302)
