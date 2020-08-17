import json

import firebase_admin
from async_spotify import SpotifyApiClient
from firebase_admin import credentials, firestore

from modules.models import Track, UnmatchedTrack
from modules.mongodb import creds
from modules.spotify import get_track_data, spotify_init

cred = credentials.Certificate("auth/google_cloud_creds.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
users = db.collection("users")
tracks = db.collection("tracks")
albums = db.collection("albums")
artists = db.collection("artists")


def insert_user(username: str, email: str):
    data = {"username": username, "email": email, "scrobbles": []}
    doc = users.document()
    doc.set(data)

    return doc.id


def is_user_new(email: str) -> bool:
    return not bool(users.where("email", "==", email))


def get_user(username: str):
    return users.where("username", "==", username)[0]


async def insert_unmatched_track(username: str, unmatched_track: UnmatchedTrack):
    matched_track = tracks.where("unmatched_name", "==", unmatched_track.name)[0]
    track_id = None

    if matched_track is None:
        client: SpotifyApiClient = await spotify_init()
        track: Track = await get_track_data(
            unmatched_track, client,
        )
        track_json: dict = json.loads(track.to_json())
        track_json["unmatched_name"] = unmatched_track.name
        doc = tracks.document()
        doc.set(track_json)
        track_id = doc.id

        await client.close_client()
    else:
        track_id = matched_track["_id"]

    users.where("username", "==", username)[0].set(
        {"scrobbles": {"time": unmatched_track.time, "track": track_id}},
        {"merge": True},
    )
