"""LastFm API wrapper"""

import asyncio
import json
import math
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Awaitable, List, Optional, Tuple
from urllib.parse import urlencode

from aiohttp import ClientResponse, ClientSession
from dataclasses_json import dataclass_json

from modules.models import Artist, Track


@dataclass
class _RecentTracks:
    total_pages: int
    current_page: int
    tracks: List[Track]


# Allows for more endpoints to be added
@dataclass
class _LastFMQuery:
    method: str = field(init=False)
    format: str = field(init=False, default="json")
    api_key: str


# @dataclass
# class _LastFMResponse:
#     query: _LastFMQuery
#     res: ClientResponse


@dataclass
class _RecentTracksQuery(_LastFMQuery):
    username: str
    page: int = field(default=1)
    limit: int = field(default=200)

    def __post_init__(self):
        self.method = "user.getRecentTracks"


def _parse_artists(artist_str: str) -> List[Artist]:
    artists_str: List[str] = artist_str.split("&")
    artists: List[Artist] = []
    for artist in artists_str:
        artists.append(Artist(artist))

    return artists


def _parse_recent_tracks(res: str) -> _RecentTracks:
    data: dict = json.loads(res)["recenttracks"]
    total_pages: int = int(data["@attr"]["totalPages"])
    current_page: int = int(data["@attr"]["page"])
    raw_tracks: List[dict] = data["track"]

    parsed_tracks: List[Track] = []

    for track in raw_tracks:
        is_playing = "@attr" in track and bool(track["@attr"]["nowplaying"])
        if is_playing:
            continue
        name: str = track["name"]
        artists: List[Artist] = _parse_artists(track["artist"]["#text"])
        album: str = track["album"]["#text"]
        art: str = track["image"][3]["#text"]
        date = int(track["date"]["uts"])
        parsed_tracks.append(Track(name, artists, album, date, image=art))

    return _RecentTracks(total_pages, current_page, parsed_tracks)


class LastFM:
    """ A LastFM Api query builder

    Args:
        api_key (str): Api key for accessing lastfm endpoint
    """

    def __init__(self, api_key: str):
        self._api_key = api_key
        self._base_url = "http://ws.audioscrobbler.com/2.0/?"

    async def _request(
        self, query: _LastFMQuery, session: ClientSession, method="GET"
    ) -> ClientResponse:
        url = self._base_url + urlencode(asdict(query))
        async with session.get(url) as res:
            if res.status != 200:
                print("RATE LIMITED")
                time.sleep(5)
                return await self._request(query, session, method)

            return await res.text()

    async def get_recent_tracks(self, username: str) -> List[Track]:
        """ Gets all scrobbled tracks by the supplied user

        Args:
            username (str): The name of the user to get the tracks from
        """
        limit = 1000
        async with ClientSession() as session:
            query = _RecentTracksQuery(self._api_key, username, limit=1)
            # TODO implement respose error handling eg.bad username
            # Have to get first page seperately to get total pages
            start_time = time.time()
            first_res: str = await self._request(query, session)
            first_page: _RecentTracks = _parse_recent_tracks(first_res)
            total_pages = math.ceil(first_page.total_pages / limit)

            recent_track_pages: List[_RecentTracks] = []
            awitable_pages: List[Awaitable[str]] = []

            for page in range(1, total_pages + 1):
                query = _RecentTracksQuery(self._api_key, username, page, limit)
                awitable_pages.append(
                    asyncio.create_task(self._request(query, session))
                )

            pages: Tuple[str] = await asyncio.gather(*awitable_pages)

            for page in pages:
                recent_track_pages.append(_parse_recent_tracks(page))
            recent_track_pages.sort(key=lambda x: x.current_page)
            recent_tracks: List[Track] = [
                item for page in recent_track_pages for item in page.tracks
            ]
            print("--- %s seconds ---" % (time.time() - start_time))

        await session.close()

        return recent_tracks


async def import_tracks(username: str):
    with open("auth/lastfm_creds.json", "r") as file:
        api_key: str = json.loads(file.read())["api_key"]

    lastfm = LastFM(api_key)
    tracks = await lastfm.get_recent_tracks(username)
