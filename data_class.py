from dataclasses import dataclass
from datetime import datetime


@dataclass
class device:
    id: int
    ip: str
    name: str
    mac: str
    active: bool
    last_online: datetime


@dataclass
class status_event:
    created: datetime
    message: str