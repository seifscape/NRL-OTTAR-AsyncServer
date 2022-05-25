import datetime
from typing import List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from database.models import CaptureAlbum, CaptureImage, CaptureImageAlbums


class CaptureAlbumDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_image(self, base64_img: str, date_created: datetime) -> CaptureImage:
        date = datetime.datetime.now()
        image = CaptureImage(encoded=base64_img, date_created=date)
        self.db_session.add(image)
        await self.db_session.commit()
        await self.db_session.refresh(image)
        # await self.db_session.flush()
        return image

    async def add_to_capture_image_album(self, image_id: int, album_id: int) -> CaptureImageAlbums:
        """Add image to capture_image_album table"""
        capture_image_album = CaptureImageAlbums(album_id=album_id, image_id=image_id)
        self.db_session.add(capture_image_album)
        await self.db_session.commit()
        await self.db_session.refresh(capture_image_album)

        return capture_image_album

    async def create_capture(self, annotation: str, coordinates: str, date_created: datetime,
                             date_updated: datetime) -> CaptureAlbum:
        date = datetime.datetime.now()
        new_capture = CaptureAlbum(annotation=annotation, coordinates=coordinates, date_created=date,
                                   date_updated=date)

        self.db_session.add(new_capture)
        await self.db_session.commit()
        await self.db_session.refresh(new_capture)
        # await self.db_session.flush()
        return new_capture

    async def get_all_captures(self) -> List[CaptureAlbum]:
        # https://stackoverflow.com/a/70105356
        query = await self.db_session.execute(
            select(CaptureAlbum).order_by(CaptureAlbum.album_id).options(selectinload(CaptureAlbum.images)))
        return query.scalars().all()

    async def get_capture_by_id(self, capture_id: int) -> CaptureAlbum:
        return await self.db_session.get(CaptureAlbum, capture_id)

    async def delete_capture_by_id(self, capture_id: int) -> bool:
        # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table
        capture = await self.get_capture_by_id(capture_id)
        result = await self.db_session.delete(capture)
        await self.db_session.flush()
        if result is None:
            return True

    async def update_capture_annotation(self, capture_id: int, update_annotation: str):
        statement = update(CaptureAlbum).where(CaptureAlbum.album_id == capture_id).values(annotation=update_annotation)
        await self.db_session.execute(statement)
        await self.db_session.commit()
