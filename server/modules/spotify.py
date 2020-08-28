import json
import re
from typing import List, Optional

from async_spotify import (
    SpotifyApiClient,
    SpotifyApiPreferences,
    SpotifyAuthorisationToken,
)

from modules.models import Album, Artist, Track, UnmatchedTrack


class RenewClass:
    async def __call__(
        self, spotify_api_client: SpotifyApiClient
    ) -> SpotifyAuthorisationToken:
        return await spotify_api_client.refresh_token()


async def spotify_init() -> SpotifyApiClient:
    with open("auth/spotify_creds.json") as readfile:
        data = json.loads(readfile.read())
        client_id = data["client_id"]
        secret = data["secret"]

    preferences = SpotifyApiPreferences(
        application_id=client_id, application_secret=secret
    )

    api_client: SpotifyApiClient = SpotifyApiClient(
        preferences, hold_authentication=True, token_renew_instance=RenewClass
    )
    await api_client.get_auth_token_with_client_credentials()
    await api_client.create_new_client(request_limit=100, request_timeout=30)

    return api_client


async def parse_spotify_track(
    track: dict, unmatched_track: UnmatchedTrack, spotify_client: SpotifyApiClient
):
    track_name: str = track["name"]
    track_preview: str = track["preview_url"]
    track_id: str = track["id"]

    album_name: str = track["album"]["name"]
    album_art: str = track["album"]["images"][0]["url"]
    album_id: str = track["album"]["id"]
    album = Album(album_name, album_art, album_id)

    artists: List[Artist] = []

    for artist in track["artists"]:
        artist_name = artist["name"]
        artist_id = artist["id"]
        artist_search = await spotify_client.artists.get_one(artist_id)
        artist_image = artist_search["images"][0]["url"]
        artist_genres = artist_search["genres"]

        artists.append(
            Artist(
                artist_name,
                spotify_id=artist_id,
                image=artist_image,
                genres=artist_genres,
            )
        )

    return Track(
        track_name, artists, unmatched_track.time, album, track_preview, track_id
    )


async def get_track_data(
    unmatched_track: UnmatchedTrack, spotify_client: SpotifyApiClient
) -> Optional[Track]:
    artists_str = [x.strip() for x in unmatched_track.artist.split("&")]
    tracks = []

    cleaned_name = re.sub("\(.*\)", "", unmatched_track.name).strip()

    for artist in artists_str:
        search = await spotify_client.search.start(
            "track:{0} artist:{1}".format(cleaned_name, artist), ["track"], limit=1,
        )
        tracks = search["tracks"]["items"]

        if tracks:
            break

    if not tracks:
        artists: List[Artist] = []
        for artist in artists_str:
            artists.append(Artist(artist))

        return Track(unmatched_track.name, artists, unmatched_track.time)

    return await parse_spotify_track(tracks[0], unmatched_track, spotify_client)


async def testing():
    client: SpotifyApiClient = await spotify_init()
    track = await get_track_data(
        UnmatchedTrack("FRIENDS (Acoustic)", "Anne-Marie & marshmello", 1000000), client
    )
    print(track)
    await client.close_client()
