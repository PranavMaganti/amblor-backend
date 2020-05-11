import binascii
import os

from flask import Flask, request, jsonify
from flask_jwt_extended import get_jwt_identity, create_access_token, JWTManager, jwt_required, \
    jwt_refresh_token_required, create_refresh_token
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from db import users, insertSong
from models import User
from spotify import Song, getSongData


def authenticate(username, password):
    user = users.find_one({"username": username})
    if user and pbkdf2_sha256.verify(password, user["password"]):
        return user

    return None


app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = binascii.hexlify(os.urandom(24))
jwt = JWTManager(app)


@app.route('/add-user', methods=['POST'])
def addUser():
    data = request.get_json()
    user = users.find_one({"username": data["username"]})
    if user is not None:
        return "User already added", 400

    user = User(data["username"], pbkdf2_sha256.encrypt(data["password"]))
    users.insert(user.to_dict())

    return "New user added", 200


@app.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({"msg": "Missing username parameter"}), 400
    if not password:
        return jsonify({"msg": "Missing password parameter"}), 400

    auth = authenticate(username, password)
    if auth is None:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@app.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200


# Datetime format ISO 8601
@app.route('/scrobble', methods=['POST'])
@jwt_required
def scrobble():
    data = request.get_json()
    user = get_jwt_identity()
    name: str = data["song"]
    artist: str = data["artist"]
    time: str = data["time"]

    song: Song = getSongData(name, artist, time)
    insertSong(user, song)

    return jsonify(logged_in_as=user), 200


if __name__ == '__main__':
    app.run()
