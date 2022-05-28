import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.data_access_layer.capture_dal import CaptureAlbumDAL
from app.data_access_layer.image_dal import CaptureImageDAL
from app.database.database import get_session, init_db
from app.database.models import CaptureAlbum, CaptureImage
from app.database.schemas import *

app = FastAPI()


@app.on_event("startup")
async def startup():
    # create db tables
    await init_db()


@app.get("/captures", response_model=Captures)
async def get_all_captures(session: AsyncSession = Depends(get_session)) -> dict[str, List[CaptureAlbum]]:
    capture_dal = CaptureAlbumDAL(session)
    captures = await capture_dal.get_all_captures()
    return {"captures": captures}


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#advanced-description-from-docstring
@app.post("/captures", response_model=Capture)
async def create_capture(capture: Capture, session: AsyncSession = Depends(get_session)):
    capture_dal = CaptureAlbumDAL(session)
    posted_capture = await capture_dal.create_capture(capture)
    # https://docs.sqlalchemy.org/en/14/orm/session_api.html?highlight=flush#sqlalchemy.orm.session.Session.flush
    # await capture_dal.db_session.flush()
    capture.album_id = posted_capture.album_id
    return capture


@app.get("/captures/{capture_id}", response_model=DetailedCapture)
async def get_capture_by_id(capture_id: int, session: AsyncSession = Depends(get_session)) -> dict[str, CaptureAlbum]:
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id=capture_id)
    if capture is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return capture


@app.put("/captures/{capture_id}")
async def update_capture_by_id(capture: Capture, capture_id: int,
                               session: AsyncSession = Depends(get_session)):
    capture_dal = CaptureAlbumDAL(session)
    return await capture_dal.update_capture(capture_id,
                                            annotation=capture.annotation,
                                            date_updated=capture.date_updated)


@app.delete("/captures/{capture_id}")
async def delete_capture_by_id(capture_id: int, session: AsyncSession = Depends(get_session)):
    capture_dal = CaptureAlbumDAL(session)
    return await capture_dal.delete_capture_by_id(capture_id=capture_id)


@app.post("/captures/{album_id}/add_image")
async def add_image_to_album(image: Image, album_id: int, session: AsyncSession = Depends(get_session)) -> Image:
    image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    album_dal = CaptureAlbumDAL(session)
    album = await album_dal.get_capture_by_id(album_id)
    # https://stackoverflow.com/questions/50026672/sql-alchemy-how-to-insert-data-into-two-tables-and-reference-foreign-key
    await image_dal.create_image(image, album)
    # await album_dal.add_to_capture_image_album(image.image_id, album_id)
    return image


@app.post("/captures/{album_id}/add_images")
async def add_images_to_album(images: CreateImages, album_id: int,
                              session: AsyncSession = Depends(get_session)):
    image_dal = CaptureImageDAL(session)
    album_dal = CaptureAlbumDAL(session)
    list_of_images = []
    album = await album_dal.get_capture_by_id(album_id)
    for i in images.images:
        capture_image = CaptureImage(encoded=i.encoded, date_created=i.date_created)
        capture_image.image_album.append(album)
        list_of_images.append(capture_image)

    image_dal.db_session.add_all(list_of_images)
    await image_dal.db_session.commit()
    await image_dal.db_session.flush()


@app.delete("/captures/{album_id}/remove_images")
async def delete_images_from_album(images: DeleteImages,
                                   session: AsyncSession = Depends(get_session)):
    image_dal = CaptureImageDAL(session)
    for i in images.image_ids:
        await image_dal.delete_image(i)


@app.post("/image", response_model=Image)
async def add_image(image: Image, session: AsyncSession = Depends(get_session)) -> CaptureImage:
    image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    await image_dal.create_image(image)
    return image


@app.delete("/images/{image_id}")
async def delete_image_by_id(image_id: int,
                             session: AsyncSession = Depends(get_session)):
    image_dal = CaptureImageDAL(session)
    return await image_dal.delete_image(image_id)


if __name__ == '__main__':
    # asyncio.run(async_main())
    uvicorn.run("server:app", port=1111, host='127.0.0.1', reload=True)
