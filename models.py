from dataclasses import dataclass, field
from typing import List

from dataclasses_json import dataclass_json

from spotify import Song


@dataclass_json
@dataclass
class User:
    username: str
    password: str
    scrobbles: List[Song] = field(default_factory=list)
