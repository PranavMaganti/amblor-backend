""" Main app """
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional

from google.auth.transport import requests
from google.oauth2 import id_token

import jwt
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError
from modules.lastfm import import_tracks
from modules.mongodb import get_user, insert_user, is_user_new
from passlib.context import CryptContext
from pydantic import BaseModel

# 1. Endpoint to check if user exists from firebase token id and return a boolean
# 2. Endpoint to check if a given username is already used
# 3. Endpoint which creates a new user from firebase token and username
# 4. Endpoint which returns an access token when supplied with a firebase token


ACCESS_TOKEN_EXPIRE_MINUTES = 15
ALGORITHM = "HS256"
with open("auth/jwt_secret.json") as readfile:
    SECRET_KEY = json.loads(readfile.read())["secret"]

with open("auth/client_ids.json") as readfile:
    CLIEND_IDS = json.loads(readfile.read())["client_ids"]

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


def _verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash(password):
    return pwd_context.hash(password)


def _create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def _create_refresh_token(data: dict):
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


async def _get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not token provided",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_user(username)
    if user is None:
        raise credentials_exception
    return user


class _Token(BaseModel):
    access_token: str
    token_type: str


@app.get("/import/lastfm/")
async def import_lastfm(username: str):
    loop = asyncio.get_event_loop()
    loop.create_task(import_tracks(username))
    return {"response": "This will take 2-3 minutes"}


@app.post("/users/add", status_code=200)
def add_user(
    login: _LoginDetails, response: Response, current_user=Depends(_get_current_user)
):
    if not ("admin" in current_user and current_user["admin"]):
        response.status_code = 403
        return {"response": "Only admins can access this endpoint"}

    if get_user(login.username) is None:
        hashed_password = _get_password_hash(login.password)
        insert_user(login.username, hashed_password)
        return {"response": "User has been added"}

    response.status_code = 400
    return {"response": "Username is already registared"}


@app.post("/token", response_model=_Token, status_code=400)
def get_access_token(login: _LoginDetails, response: Response):
    user = get_user(login.username)
    if user is None:
        return {"response": "Invalid username entered"}

    if _verify_password(login.password, user["password"]):
        response.status_code = 200
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = _create_access_token(
            data={"sub": user["username"]}, expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}

    return {"response": "Invalid password entered "}


@app.post("/user/firebase/new")
async def is_new_user(request: Request, response: Response):
    body = await request.body()
    try:
        idinfo = id_token.verify_firebase_token(body, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            userid = idinfo["sub"]
            new = is_user_new(idinfo["email"])
            return new
        else:
            response.status_code = 400
            return "The request was made from an invalid client"
    except ValueError:
        response.status_code = 400
        return "The token supplied was invalid"


@app.get("/users/create/{username}")
async def add_new_user(
    username: str, request: Request,
):
    body = await request.body()
    try:
        idinfo = id_token.verify_firebase_token(body, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            userid = idinfo["sub"]
            new = is_user_new(idinfo["email"])
            return new
        else:
            response.status_code = 400
            return "The request was made from an invalid client"
    except ValueError:
        response.status_code = 400
        return "The token supplied was invalid"


@app.get("/users/{username}")
async def get_user_info(username: str, current_user=Depends(_get_current_user)):
    if username != current_user["username"]:
        return {"response": "Not logged in as {0}".format(username)}
    return {
        "username": current_user["username"],
        "scrobbles": current_user["scrobbles"],
    }
