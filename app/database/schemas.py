from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class Image(BaseModel):
    image_id: Optional[int]
    encoded: str
    date_created: datetime

    class Config:
        orm_mode = True


class DeleteImages(BaseModel):
    image_ids: List[int]


class CreateImages(BaseModel):
    images: Union[List[Image], None] = None


class Capture(BaseModel):
    album_id: Optional[int]
    annotation: str
    coordinates: str
    date_created: datetime
    date_updated: datetime

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class DetailedCapture(Capture):
    images: Union[Optional[List[Image]]] = None

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class Captures(BaseModel):
    captures: List[Capture]

    class Config:
        orm_mode = True
