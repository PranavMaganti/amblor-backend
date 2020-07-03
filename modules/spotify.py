"""Spotify API wrapper"""

import asyncio
import copy
import json
import time
from dataclasses import asdict, dataclass, field
from typing import Awaitable, Dict, List, Optional
from urllib.parse import urlencode

import requests
from aiohttp import ClientSession, TCPConnector
from dataclasses_json import dataclass_json
from requests.auth import HTTPBasicAuth

from lastfm import import_tracks
from models import Artist, Track
from models import Album


@dataclass
class _SearchQuery:
    query: str
    type: str = field(default="track")
    limit: int = field(default=3)


@dataclass_json
@dataclass
class SpotifyClientCredentials:
    """ Data class to store credentials for accessing Spotify API"""

    client_id: str
    secret: str
    headers: Dict = field(init=False)

    def __post_init__(self):
        self.get_access_token()

    def get_access_token(self):
        """ Gets a client access token for API"""
        token_endpoint = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        res = requests.post(
            token_endpoint, auth=HTTPBasicAuth(self.client_id, self.secret), data=data
        )

        access_token = json.loads(res.text)["access_token"]
        self.headers = {"Authorization": "Bearer " + access_token}


def _parse_tracks_info(info: Dict, original_track: Track) -> Track:
    tracks: List[Dict] = info["tracks"]["items"]

    if len(tracks) == 0:
        return original_track

    target_track: Optional[Dict] = None
    for track in tracks:
        if track["name"] == original_track.name:
            target_track = track
            break

        target_artist = original_track.artists[0].name
        match = False
        for matched_artist in track["artists"]:
            if target_artist.lower() == matched_artist["name"].lower():
                match = True
                break

        if match:
            target_track = track
        else:
            break

    if target_track is None:
        return original_track

    track_name: str = target_track["name"]
    track_preview: str = target_track["preview_url"]
    track_id: str = target_track["id"]

    album_name: str = target_track["album"]["name"]
    album_art: str = target_track["album"]["images"][0]["url"]
    album_id: str = target_track["album"]["id"]
    album = Album(album_name, album_art, album_id)

    artists: List[Artist] = []

    for artist in target_track["artists"]:
        artist_name = artist["name"]
        artist_id = artist["id"]

        artists.append(Artist(artist_name, artist_id))

    return Track(
        track_name, artists, original_track.time, album, track_preview, track_id
    )


class Spotify:
    """ Spotify API query builder """

    def __init__(self, client_creds: SpotifyClientCredentials):
        self._creds = client_creds
        self._base_url = "https://api.spotify.com/v1/"
        self._total = 0
        self._sleep = 0

    async def _search_request(
        self, query: _SearchQuery, session: ClientSession, counter: int = 0
    ) -> str:
        url = self._base_url + "search?" + urlencode(asdict(query))
        time.sleep(self._sleep)
        async with session.get(url) as res:
            if res.status != 200:
                if counter > 3:
                    raise KeyError
                print(await res.text())
                if res.status == 401:
                    self._creds.get_access_token()
                elif res.status == 429:
                    print(res.headers["Retry-After"])
                    self._sleep = int(res.headers["Retry-After"])
                    time.sleep(int(res.headers["Retry-After"]))
                else:
                    asyncio.sleep(60)

                self._sleep = 0
                return await self._search_request(query, session, counter + 1)
            else:
                self._total += 1
                print(self._total)
            return await res.text()

    async def get_track_info(self, track: Track, session: ClientSession) -> Track:
        """ Queries and parses track info from spotify API """
        query_str: str = ("track:{0} artist:{1}").format(
            track.name, track.artists[0].name
        )
        query = _SearchQuery(query_str)
        tracks_data: Dict = json.loads(await self._search_request(query, session))

        if len(tracks_data["tracks"]["items"]) == 0:
            query_str: str = ("track:{0}").format(track.name)
            query = _SearchQuery(query_str)
            tracks_data: Dict = json.loads(await self._search_request(query, session))

        return _parse_tracks_info(tracks_data, track)

    def get_auth_headers(self) -> Dict[str, str]:
        return self._creds.headers


async def match_lastfm_tracks(tracks: List[Track]):
    """ Matches metadata of lastfm scrobbles with a tracks on spotify """
    with open("auth/spotify_creds.json") as data_file:
        creds: SpotifyClientCredentials = SpotifyClientCredentials.from_json(
            data_file.read()
        )
    spotify = Spotify(creds)

    # Get rid of duplicates
    track_map: Dict[str, Track] = {}
    for track in tracks:
        track_map[track.name] = copy.deepcopy(track)

    conn = TCPConnector(limit=10)
    async with ClientSession(
        headers=spotify.get_auth_headers(), connector=conn
    ) as session:
        awaitable_tracks: Dict[str, Track] = {}
        for key in track_map:
            track = track_map[key]
            awaitable_tracks[key] = asyncio.create_task(
                spotify.get_track_info(track, session)
            )

        await asyncio.gather(*(awaitable_tracks.values()))

        for key in awaitable_tracks:
            awaitable_track: Awaitable[Track] = awaitable_tracks[key]
            track_map[key] = await awaitable_track
        hello = "Hello"


loop = asyncio.get_event_loop()
import_tracks = loop.run_until_complete(import_tracks("vanpra"))
matched = loop.run_until_complete(match_lastfm_tracks(import_tracks))
