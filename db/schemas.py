from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class Image(BaseModel):
    date_created: datetime
    image_id: int
    encoded: str

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
    images: Optional[List[Image]]

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class Captures(BaseModel):
    captures: List[Capture]

    class Config:
        orm_mode = True
