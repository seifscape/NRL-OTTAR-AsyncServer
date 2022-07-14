from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class CreateImage(BaseModel):
    capture_id: Optional[int]
    encoded: str
    date_created: Optional[datetime]


class Image(CreateImage):
    image_id: int

    class Config:
        orm_mode = True


class DeleteImages(BaseModel):
    image_ids: List[int]


class CreateImages(BaseModel):
    images: Union[List[CreateImage], None] = None


class Images(BaseModel):
    images: List[Image]

    class Config:
        orm_mode = True


class CreateAndUpdateCapture(BaseModel):
    annotation: str
    coordinates: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    images: Union[Optional[List[CreateImage]]] = None


class Capture(CreateAndUpdateCapture):
    capture_id: int
    images: Union[Optional[List[Image]]] = None

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class Captures(BaseModel):
    captures: List[Capture]

    class Config:
        orm_mode = True
