"""Spotify API wrapper"""

import asyncio
import json
from os import sendfile
import time
from dataclasses import asdict, dataclass, field
from typing import List
from urllib.parse import urlencode

import requests
from aiohttp import ClientResponse, ClientSession
from dataclasses_json import dataclass_json
from requests.auth import HTTPBasicAuth
from modules.models import Track, Artist


@dataclass
class _SearchQuery:
    query: str
    type: str = field(default="track")
    limit: int = field(default=1)


@dataclass_json
@dataclass
class SpotifyClientCredentials:
    """ Data class to store credentials for accessing Spotify API"""

    client_id: str
    secret: str
    access_token: str = field(init=False)

    def __post_init__(self):
        token_endpoint = "https://accounts.spotify.com/api/token"
        data = {"grant_type": "client_credentials"}
        res = requests.post(
            token_endpoint, auth=HTTPBasicAuth(self.client_id, self.secret), data=data
        )

        self.access_token = json.loads(res.text)["access_token"]


class Spotify:
    """ Spotify API query builder """

    def __init__(self, client_creds: SpotifyClientCredentials):
        self._creds = client_creds
        self._base_url = "https://api.spotify.com/v1/"
        self._headers = {"Authorization": "Bearer " + self._creds.access_token}

    async def _search_request(
        self, query: _SearchQuery, session: ClientSession
    ) -> ClientResponse:
        url = self._base_url + "search?" + urlencode(asdict(query))
        async with session.get(url) as res:
            if res.status != 200:
                print(await res.text())
                if res.status == 429:
                    print("RATE LIMIT")
                    time.sleep(int(res.headers["Retry-After"]))
                else:
                    time.sleep(60)
                return await self._search_request(query, session)

            return await res.text()

    async def get_track_info(self, track: str, artist: str):
        query_str: str = ("track:{0} artist:{1}").format(track, artist)
        query = _SearchQuery(query_str)
        async with ClientSession(headers=self._headers) as session:
            data: str = await self._search_request(query, session)
            print(data)


def match_lastfm_tracks(tracks: List[Track]):


with open("auth/spotify_creds.json") as data_file:
    creds: SpotifyClientCredentials = SpotifyClientCredentials.from_json(
        data_file.read()
    )

print(creds.access_token)

spotify = Spotify(creds)


loop = asyncio.get_event_loop()
loop.run_until_complete(spotify.get_track_info("FRIENDS(Acoustic)", ""))

