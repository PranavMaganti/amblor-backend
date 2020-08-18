""" Main app """
import asyncio
import json
from datetime import datetime, timedelta

import jwt
from dataclasses_json.api import dataclass_json
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from jwt import PyJWTError
from pydantic import BaseModel

from modules.mysql import get_user, insert_user, is_user_new, is_username_taken
from modules.lastfm import import_tracks

# 460 - Username Taken (create user endpoint)

# 1. Endpoint to check if user exists from firebase token id and return a boolean
# 3. Endpoint which creates a new user from firebase token and username (Returns 460 if username is taken)
# 4. Endpoint which returns an access token when supplied with a firebase token

ACCESS_TOKEN_EXPIRE_MINUTES = 15
ALGORITHM = "HS256"
with open("auth/jwt_secret.json") as readfile:
    SECRET_KEY = json.loads(readfile.read())["secret"]

with open("auth/client_ids.json") as readfile:
    CLIEND_IDS = json.loads(readfile.read())["client_ids"]

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")


@dataclass_json
class _Token:
    access_token: str
    refresh_token: str
    expires_at: int
    token_type: str


class _AddUserRequest(BaseModel):
    username: str
    firebase_token: str


def _create_token(data: dict, expire_time: int = None) -> str:
    to_encode = data.copy()
    if expire_time != None:
        expire = datetime.utcnow() + timedelta(minutes=expire_time)
        to_encode.update({"exp": expire})
    return str(jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM))


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


def _error(message: str) -> dict:
    return {"error": message}


@app.get("/import/lastfm/")
async def import_lastfm(username: str):
    loop = asyncio.get_event_loop()
    loop.create_task(import_tracks(username))
    return {"response": "This will take 2-3 minutes"}


@app.post("/token")
async def get_token(request: Request, response: Response):
    body = await request.body()
    try:
        idinfo = id_token.verify_firebase_token(body, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            email = {"sub": idinfo["email"]}
            access_token = _create_token(email, ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token = _create_token(email)
            expires_at = (datetime.utcnow() + timedelta(minutes=15)).timestamp
            return _Token(access_token, refresh_token, expires_at, "Bearer").to_json()
        else:
            response.status_code = 401
            return _error("The request was made from an invalid client")
    except ValueError:
        response.status_code = 422
        return _error("The token supplied was invalid")


# Returns boolean dependant on if the user is new
@app.post("/users/add")
async def user_exists(user: _AddUserRequest, response: Response):
    if is_username_taken(user.username):
        response.status_code = 409
        return _error("Username taken")

    try:
        idinfo = id_token.verify_firebase_token(user.firebase_token, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            insert_user(user.username, idinfo["email"])
            return {"success": "User Added"}
        else:
            response.status_code = 401
            return _error("The request was made from an invalid client")

    except ValueError:
        response.status_code = 422
        return _error("The token supplied was invalid")


# Returns boolean dependant on if the user is new
@app.post("/users")
async def user_exists(request: Request, response: Response):
    body = await request.body()
    try:
        idinfo = id_token.verify_firebase_token(body, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            return is_user_new(idinfo["email"])
        else:
            response.status_code = 401
            return _error("The request was made from an invalid client")
    except ValueError:
        response.status_code = 422
        return _error("The token supplied was invalid")
