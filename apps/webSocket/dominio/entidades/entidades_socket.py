from dataclasses import dataclass
from typing import Optional


@dataclass
class CallEvent:
    event_type: str
    username: str
    message: str
    joined: Optional[bool] = False
    left: Optional[bool] = False
