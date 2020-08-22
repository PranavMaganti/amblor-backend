""" Main app """
import asyncio
import json
from datetime import datetime, timedelta
from typing import List

import jwt
from async_spotify import SpotifyApiClient
from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import Response
from fastapi.security import OAuth2PasswordBearer
from google.auth.transport import requests
from google.oauth2 import id_token
from jwt import PyJWTError
from pydantic import BaseModel

from modules.lastfm import import_tracks
from modules.models import UnmatchedTrack
from modules.mysql import (get_scrobbles, insert_scrobble, insert_user, is_user_new,
                           is_username_taken)
from modules.spotify import get_track_data, spotify_init

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class _Token(BaseModel):
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

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM).decode("utf-8")


async def _get_current_user(access_token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not user token provided",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(access_token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except PyJWTError:
        raise credentials_exception
    user = get_scrobbles(email)
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


@app.post("/token", response_model=_Token)
async def get_token(request: Request, response: Response):
    body = await request.body()
    try:
        idinfo = id_token.verify_firebase_token(body, requests.Request())
        if idinfo["aud"] in CLIEND_IDS:
            email = {"sub": idinfo["email"]}
            access_token = _create_token(email, ACCESS_TOKEN_EXPIRE_MINUTES)
            refresh_token = _create_token(email)
            expires_at = (datetime.utcnow() + timedelta(minutes=15)).timestamp()
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "token_type": "Bearer",
            }

        else:
            response.status_code = 401
            return _error("The request was made from an invalid client")
    except ValueError:
        response.status_code = 422
        return _error("The token supplied was invalid")


# Returns boolean dependant on if the user is new
@app.post("/user/add")
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
@app.post("/user")
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


@app.get("/user/scrobbles")
async def get_user_scrobbles(current_user: str = Depends(_get_current_user)):
    return get_scrobbles(current_user)


@app.post("/user/scrobbles")
async def add_user_scrobble(
    track_name: str, artist_name: str, time: int, current_user: str = Depends(_get_current_user)
):
    client: SpotifyApiClient = await spotify_init()
    track = await get_track_data(
        UnmatchedTrack(track_name, artist_name, time), client
    )
    print(track)
    insert_scrobble(track, current_user)
    await client.close_client()
