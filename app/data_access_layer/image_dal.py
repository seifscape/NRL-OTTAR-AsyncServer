from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import CaptureImage, CaptureAlbum
from sqlalchemy import delete


class CaptureImageDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_image(self, capture_image: CaptureImage,
                           capture_album: CaptureAlbum) -> CaptureImage:
        image = capture_image
        image.capture_album.append(capture_album)
        self.db_session.add(image)
        await self.db_session.commit()
        await self.db_session.refresh(image)
        return image

    async def delete_image(self, image_id):
        statement = delete(CaptureImage).where(CaptureImage.image_id == image_id).\
            execution_options(synchronize_session="fetch")
        await self.db_session.execute(statement)

