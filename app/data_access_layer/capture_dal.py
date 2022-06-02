import datetime
from typing import List

from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database.models import CaptureAlbum, CaptureImage, CaptureImageAlbums
from app.database.schemas import Capture


class CaptureAlbumDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_image(self, capture_image: CaptureImage) -> CaptureImage:
        date = datetime.datetime.now()
        image = CaptureImage(encoded=capture_image.encoded, date_created=date)
        self.db_session.add(capture_image)
        await self.db_session.commit()
        await self.db_session.refresh(capture_image)
        # await self.db_session.flush()
        return image

    async def add_to_capture_image_album(self, image_id: int, album_id: int) -> CaptureImageAlbums:
        """Add image to capture_image_album table"""
        capture_image_album = CaptureImageAlbums(album_id=album_id, image_id=image_id)
        self.db_session.add(capture_image_album)
        await self.db_session.commit()
        await self.db_session.refresh(capture_image_album)

        return capture_image_album

    async def create_capture(self, capture: Capture) -> CaptureAlbum:
        date = datetime.datetime.now()
        new_capture = CaptureAlbum(annotation=capture.annotation, coordinates=capture.coordinates,
                                   date_created=capture.date_created, date_updated=capture.date_updated)
        capture.date_created = date
        self.db_session.add(new_capture)
        await self.db_session.commit()
        await self.db_session.refresh(new_capture)
        # https://docs.sqlalchemy.org/en/14/orm/session_api.html#sqlalchemy.orm.Session.flush
        # await self.db_session.flush()
        return new_capture

    async def get_all_captures(self) -> List[CaptureAlbum]:
        # https://stackoverflow.com/a/70105356
        query = await self.db_session.execute(
            select(CaptureAlbum).order_by(CaptureAlbum.album_id).options(selectinload(CaptureAlbum.images)))
        return query.scalars().all()

    async def get_capture_by_id(self, capture_id: int) -> CaptureAlbum:
        return await self.db_session.get(CaptureAlbum, capture_id)

    async def delete_capture_by_id(self, capture_id: int):
        # https://docs.sqlalchemy.org/en/14/orm/basic_relationships.html#deleting-rows-from-the-many-to-many-table
        capture = await self.get_capture_by_id(capture_id)
        result = await self.db_session.delete(capture)
        await self.db_session.commit()
        await self.db_session.flush()


    async def update_capture(self, capture_id: int, **kwargs):
        statement = update(CaptureAlbum)\
            .where(CaptureAlbum.album_id == capture_id).\
            values(**kwargs).\
            execution_options(synchronize_session="fetch")
        await self.db_session.execute(statement)
        await self.db_session.commit()
