from __future__ import annotations
from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel


class Image(BaseModel):
    image_id: int
    encoded:  str
    date_created: Optional[datetime]

    class Config:
        orm_mode = True


class CreateImage(Image):
    capture_id: Optional[int]
    image_id: Optional[int]
    encoded: str
    date_created: Optional[datetime]


class ImageDeletion(Image):
    image_id: int
    encoded:  Optional[str]
    date_created: Optional[datetime]


class DeleteImages(BaseModel):
    # images: Union[List[ImageDeletion], None] = None
    image_ids: List[int]


class CreateImages(BaseModel):
    images: Union[List[CreateImage], None] = None


class Capture(BaseModel):
    capture_id: Optional[int]
    annotation: str
    coordinates: Optional[str]
    date_created: Optional[datetime]
    date_updated: Optional[datetime]
    images: Union[Optional[List[Image]]] = None

    class Config:
        arbitrary_types_allowed = True
        orm_mode = True


class Captures(BaseModel):
    captures: List[Capture]

    class Config:
        orm_mode = True
