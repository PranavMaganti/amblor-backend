import json

from async_spotify import SpotifyApiClient
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from modules.models import Track, UnmatchedTrack
from modules.spotify import get_track_data, spotify_init

with open("auth/mongodb_creds.json", "r") as file:
    creds = json.loads(file.read())
    db_username: str = creds["username"]
    db_password: str = creds["password"]

mongo_client = MongoClient(
    "mongodb+srv://{0}:{1}@cluster0.c9oms.mongodb.net/test".format(
        db_username, db_password
    )
)

db: Database = mongo_client.main
users: Collection = db.users
tracks: Collection = db.tracks
albums: Collection = db.albums
artists: Collection = db.artists


def insert_user(username: str, hashed_password: str):
    data = {"username": username, "password": hashed_password, "scrobbles": []}

    return users.insert_one(data).inserted_id


def get_user(username: str):
    return users.find_one({"username": username})


async def insert_unmatched_track(username: str, unmatched_track: UnmatchedTrack):
    matched_track = tracks.find_one({"unmatched_name": unmatched_track.name})
    track_id = None

    if matched_track is None:
        client: SpotifyApiClient = await spotify_init()
        track: Track = await get_track_data(
            UnmatchedTrack("FRIENDS (Acoustic)", "Anne-Marie & marshmello", 1000000),
            client,
        )
        track_json: dict = json.loads(track.to_json())
        track_json["unmatched_name"] = unmatched_track.name
        track_id = tracks.insert_one(track_json).inserted_id

        await client.close_client()
    else:
        track_id = matched_track["_id"]

    users.find_one_and_update(
        {"username": username},
        {"$push": {"scrobbles": {"time": unmatched_track.time, "track": track_id}}},
    )


# loop = asyncio.get_event_loop()
# task = loop.create_task(
#     insert_unmatched_track(
#         "pranav",
#         UnmatchedTrack("FRIENDS (Acoustic)", "Anne-Marie & marshmello", 1000001),
#     )
# )
# loop.run_until_complete(task)
