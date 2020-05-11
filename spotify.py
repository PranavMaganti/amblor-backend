import json
from dataclasses import dataclass
from typing import List

import spotipy
from dataclasses_json import dataclass_json
from spotipy.oauth2 import SpotifyClientCredentials


@dataclass_json
@dataclass
class Artist:
    id: str
    name: str
    image: str
    genres: List[str]


@dataclass_json
@dataclass
class Song:
    id: str
    name: str
    artists: List[Artist]
    image: str
    preview: str
    time: str


with open('auth/spotify_creds.json') as data_file:
    creds = json.load(data_file)

clientCreds = SpotifyClientCredentials(creds["client_id"], creds["secret"])
sp = spotipy.Spotify(client_credentials_manager=clientCreds)


def parseTrack(res: json, time: str) -> Song:
    track = res["tracks"]["items"][0]
    albumArt = track["album"]["images"][0]["url"]

    rawArtists: json = track["artists"]
    artists: List[Artist] = []

    for artist in rawArtists:
        artistID = artist["id"]
        name = artist["name"]
        artistData = sp.artist(artistID)
        artistImg = artistData["images"][0]["url"]
        genres = artistData["genres"]

        artists.append(Artist(artistID, name, artistImg, genres))

    return Song(track["id"], track["name"], artists, albumArt, track["preview_url"], time)


def getSongData(song: str, artist: str, time: str):
    query = "track:{0} artist:{1}".format(song, artist)
    res: json = sp.search(query, type="track", limit=1)

    return parseTrack(res, time)
