""" Common dataclasses used in modules - included mbid in case it is needed later"""

from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json
from pydantic import BaseModel


@dataclass_json
@dataclass
class Artist:
    """ Data class to store artist data """

    name: str
    image: Optional[str] = field(default=None)
    genres: Optional[List[str]] = field(default=None)
    spotify_id: Optional[str] = field(default=None)
    mbid: Optional[str] = field(default=None)
    metadata_matched: bool = field(default=False)


@dataclass_json
@dataclass
class Album:
    """ Data class to store album data """

    name: str
    image: Optional[str] = field(default=None)
    spotify_id: Optional[str] = field(default=None)
    mbid: Optional[str] = field(default=None)
    metadata_matched: bool = field(default=False)


@dataclass_json
@dataclass
class Track:
    """ Data class to store matched track data """

    name: str
    artists: List[Artist]
    time: float  # Scrobble time
    album: Optional[Album] = field(default=None)
    preview: Optional[str] = field(default=None)
    spotify_id: Optional[str] = field(default=None)
    mbid: Optional[str] = field(default=None)
    metadata_matched: bool = field(default=False)


@dataclass
class UnmatchedTrack:
    """ Data class to store unmatched track data """

    name: str
    artist: str
    time: float
