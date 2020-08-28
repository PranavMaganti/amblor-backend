import random
import string
from typing import Optional, Tuple

from modules.models import RawScrobble, Track


def none_or_str(text: str) -> Optional[str]:
    """ Returns None if string is empty and the string otherwise """
    if text == "":
        return None

    return text

def track_to_scrobble(t: Track) -> RawScrobble:
    artist_names = []
    artist_images = []
    artist_genres = []

    for item in t.artists:
        artist_names.append(item.name)
        artist_images.append(item.image)
        artist_genres.append(",".join(item.genres))

    return RawScrobble(t.time, t.name, t.preview, t.album.name, t.album.image,
    "/".join(artist_names), " ".join(artist_images), "/".join(artist_genres))
