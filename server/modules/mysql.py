import json
from typing import List, Optional

import pymysql
import pymysql.cursors

from modules.models import Album, Artist, RawScrobble, Track
from modules.queries import *

with open("auth/cloud_sql.json", "r") as file:
    creds = json.loads(file.read())
    db_username: str = creds["user"]
    db_password: str = creds["password"]
    db_host: str = creds["host"]


def create_connection() -> pymysql.Connection:
    return pymysql.connect(
        host=db_host,
        user=db_username,
        password=db_password,
        db="amblor",
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def insert_user(connection: pymysql.Connection, username: str, email: str) -> int:
    with connection.cursor() as cursor:
        sql = "INSERT INTO User (username, email) VALUES (%s, %s)"
        cursor.execute(sql, (username, email))
        connection.commit()
    return cursor.lastrowid


def is_user_new(connection: pymysql.Connection, email: str) -> bool:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE email=%s"
        cursor.execute(sql, (email,))
        connection.commit()
        result = cursor.fetchall()
    return not result


def is_username_taken(connection: pymysql.Connection, username: str) -> bool:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE username=%s"
        cursor.execute(sql, (username,))
        connection.commit()
        result = cursor.fetchall()
    return bool(result)


def get_user(connection: pymysql.Connection, email: str):
    with connection.cursor() as cursor:
        sql = "SELECT * FROM User WHERE email=%s"
        cursor.execute(sql, (email,))
        connection.commit()
        result = cursor.fetchone()
    return result


def get_scrobbles(connection: pymysql.Connection, email: str, start_time: int):
    with connection.cursor() as cursor:
        with open("queries/select.sql", "r") as readfile:
            sql = " ".join(readfile.read().split())
            where_clause = "WHERE email='%s' AND Scrobble.time>%i" % (email, start_time)
            cursor.execute(sql + " " + where_clause)
            connection.commit()
            result = cursor.fetchall()

    return result


def _insert_album(cursor: pymysql.cursors.Cursor, album: Album) -> int:
    print(album)
    album_query = get_album % (album.spotify_id)
    cursor.execute(album_query)
    fetched_album = cursor.fetchone()
    album_id = 0

    if not fetched_album:
        album_insert_query = insert_album % (album.name, album.image, album.spotify_id,)
        cursor.execute(album_insert_query)
        album_id = cursor.lastrowid
    else:
        album_id = fetched_album["album_id"]

    return album_id


def _insert_artists(cursor: pymysql.cursors.Cursor, artists: List[Artist]) -> List[int]:
    artist_ids = []
    for artist in artists:
        artist_query = get_artist % (artist.spotify_id)
        cursor.execute(artist_query)
        fetched_artist = cursor.fetchone()

        if not fetched_artist:
            cursor.execute(get_last_genre_set)
            genre_set = cursor.fetchone()
            set_id = 1
            if genre_set:
                set_id = genre_set["set_id"] + 1

            for genre in artist.genres:
                insert_genre_query = insert_genre_set % (genre, set_id)
                cursor.execute(insert_genre_query)

            artist_insert_query = insert_artist % (
                artist.name,
                set_id,
                artist.image,
                artist.spotify_id,
            )
            cursor.execute(artist_insert_query)
            artist_ids.append(cursor.lastrowid)
        else:
            artist_ids.append(fetched_artist["artist_id"])

    return artist_ids


def _insert_artist_set(cursor: pymysql.cursors.Cursor, artist_ids: List[int]) -> int:
    cursor.execute(get_last_artist_set)
    artist_set = cursor.fetchone()
    artist_set_id = 1
    if artist_set:
        artist_set_id = artist_set["set_id"] + 1

    for artist_id in artist_ids:
        artist_set_query = insert_artist_set % (artist_id, artist_set_id)
        cursor.execute(artist_set_query)

    return artist_set_id


def insert_scrobble(
    connection: pymysql.Connection,
    track: Track,
    email: str,
    time: int,
    unmatched_name: str,
) -> RawScrobble:
    with connection.cursor() as cursor:
        album_id = _insert_album(cursor, track.album)
        artist_ids = _insert_artists(cursor, track.artists)
        artist_set_id = _insert_artist_set(cursor, artist_ids)

        insert_track_query = insert_track % (
            artist_set_id,
            track.name,
            unmatched_name,
            album_id,
            track.spotify_id,
            track.preview,
        )
        cursor.execute(insert_track_query)
        track_id = cursor.lastrowid

        user = get_user(email)
        user_id = user["user_id"]
        insert_scrobble_query = insert_scrobble_entry % (user_id, track_id, time)
        cursor.execute(insert_scrobble_query)
        scrobble_id = cursor.lastrowid

        connection.commit()

        with open("queries/select.sql", "r") as readfile:
            scrobble_query = " ".join(readfile.read().split())
            where_clause = "WHERE Scrobble.scrobble_id=%i" % (scrobble_id)
            cursor.execute(scrobble_query + " " + where_clause)
            connection.commit()
            result = cursor.fetchone()

    return result


def insert_matched_scrobble(
    connection: pymysql.Connection, email: str, track_id: int, time: int
):
    with connection.cursor() as cursor:
        user_query = "SELECT user_id FROM User WHERE email=%s"
        cursor.execute(user_query, (email,))
        user_id = cursor.fetchone()["user_id"]

        insert_query = (
            "INSERT INTO Scrobble (user_id, track_id, time) VALUES (%i, %i, %i)"
            % (user_id, track_id, time)
        )
        cursor.execute(insert_query)
        inserted_id = cursor.lastrowid
        connection.commit()

        with open("queries/select.sql", "r") as readfile:
            scrobble_query = " ".join(readfile.read().split())
            where_clause = "WHERE Scrobble.scrobble_id=%i" % (inserted_id)
            cursor.execute(scrobble_query + " " + where_clause)
            result = cursor.fetchone()

        connection.commit()

    return result


def get_matched_track(
    connection: pymysql.Connection, unmatched_name: str
) -> Optional[RawScrobble]:
    with connection.cursor() as cursor:
        sql = "SELECT * FROM Track WHERE Track.unmatched_name='%s'" % (unmatched_name)
        cursor.execute(sql)
        result = cursor.fetchone()

    return result
