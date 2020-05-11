import json

from pymongo import MongoClient

from spotify import Song

with open('auth/mongodb_creds.json') as data_file:
    creds = json.load(data_file)

url = "mongodb+srv://{0}:{1}@cluster0-pg2ld.mongodb.net/test?retryWrites=true&w=majority"
client = MongoClient(url.format(creds["username"], creds["password"]))

db = client['scrobbler']
users = db["users"]


def insertSong(user: str, song: Song):
    users.update_one({"username": user},
                     {"$push": {"scrobbles": song.to_dict()}})
