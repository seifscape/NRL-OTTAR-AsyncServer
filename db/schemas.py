from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Image(BaseModel):
    image_id: Optional[int]
    encoded: str
    date_created: datetime

    class Config:
        orm_mode = True


class Capture(BaseModel):
    album_id: Optional[int]
    annotation: str
    coordinates: str
    date_created: datetime

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class DetailedCapture(Capture):
    date_updated: datetime
    images: Optional[List[Image]] = None

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class Captures(BaseModel):
    captures: List[Capture]

    class Config:
        orm_mode = True
