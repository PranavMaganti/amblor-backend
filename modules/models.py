from dataclasses import dataclass, field
from typing import List, Optional

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Artist:
    """ Data class to store artist data recived from spotify API """

    name: str
    image: Optional[str] = field(default=None)
    genres: Optional[List[str]] = field(default=None)


@dataclass_json
@dataclass
class Track:
    """ Data class to store song data recived from spotify API """

    name: str
    artists: List[Artist]
    album: str
    time: float  # Scrobble time
    image: Optional[str] = field(default=None)
    preview: Optional[str] = field(default=None)
