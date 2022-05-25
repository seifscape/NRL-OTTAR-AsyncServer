import base64
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from database.models import CaptureImage, CaptureAlbum
from sqlalchemy import delete


class CaptureImageDAL:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_image(self, capture_image: CaptureImage,
                           capture_album: Optional[CaptureAlbum] = None) -> CaptureImage:
        image = capture_image
        image.image_album.append(capture_album)
        self.db_session.add(image)

        await self.db_session.commit()
        await self.db_session.refresh(image)
        return image

    async def delete_image(self, image_id):
        statement = delete(CaptureImage).where(CaptureImage.image_id == image_id)
        result = await self.db_session.execute(statement)
        await self.db_session.commit()
        await self.db_session.flush()
        # image = self.db_session.get(CaptureImage, image_id)
        # await self.db_session.delete(image)
        # res = make_response(jsonify({}), 204)

    def is_base64(self, sb: str) -> bool:
        try:
            if isinstance(sb, str):
                # If there's any unicode here, an exception will be thrown and the function will return false
                sb_bytes = bytes(sb, 'ascii')
            elif isinstance(sb, bytes):
                sb_bytes = sb
            else:
                raise ValueError("Argument must be string or bytes")
            return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
            return False
