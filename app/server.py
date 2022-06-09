import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader, APIKey
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.status import HTTP_403_FORBIDDEN

from app.data_access_layer.capture_dal import CaptureAlbumDAL
from app.data_access_layer.image_dal import CaptureImageDAL
from app.database.database import get_session, init_db
from app.database.models import CaptureAlbum, CaptureImage
from app.database.schemas import *

app = FastAPI()

API_KEY = "nrl_ottar_2022"
API_KEY_NAME = "Authorization"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    else:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN, detail="Could not validate credentials"
        )


@app.on_event("startup")
async def startup():
    # create db tables
    await init_db()


# https://github.com/tiangolo/fastapi/issues/2007#issuecomment-747828636
@app.get("/captures", response_model=Captures, response_model_exclude={'captures': {'__all__': {'images'}}})
async def get_all_captures(session: AsyncSession = Depends(get_session),
                           _api_key: APIKey = Depends(get_api_key)) -> \
        dict[str, List[CaptureAlbum]]:
    capture_dal = CaptureAlbumDAL(session)
    captures = await capture_dal.get_all_captures()
    for i in captures:
        if i.date_updated is not None:
            i.date_updated = i.date_updated.replace(microsecond=0)
    return {"captures": captures}


# https://fastapi.tiangolo.com/advanced/path-operation-advanced-configuration/#advanced-description-from-docstring
@app.post("/capture", response_model=Capture)
async def create_capture(capture: Capture, session: AsyncSession = Depends(get_session),
                         _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    capture.date_created = datetime.now().utcnow().replace(microsecond=0)
    posted_capture = await capture_dal.create_capture(capture)
    # await capture_dal.db_session.flush()
    capture.capture_id = posted_capture.capture_id
    if capture.images is not None:
        image_dal = CaptureImageDAL(session)
        _capture = await capture_dal.get_capture_by_id(posted_capture.capture_id)
        list_of_images = []
        for i in capture.images:
            capture_image = CaptureImage(encoded=i.encoded, date_created=i.date_created)
            capture_image.image_album.append(_capture)
            list_of_images.append(capture_image)
        image_dal.db_session.add_all(list_of_images)
        await image_dal.db_session.commit()
        await image_dal.db_session.flush()
        return _capture
    else:
        return capture


@app.get("/captures/{capture_id}", response_model=Capture)
async def get_capture_by_id(capture_id: int, session: AsyncSession = Depends(get_session),
                            _api_key: APIKey = Depends(get_api_key)) -> dict[str, CaptureAlbum]:
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id=capture_id)
    if capture.date_updated is not None:
        capture.date_updated = capture.date_updated.replace(microsecond=0)
    if capture is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return capture


@app.patch("/captures/{capture_id}")
async def update_capture_by_id(capture: Capture, capture_id: int,
                               session: AsyncSession = Depends(get_session),
                               _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    return await capture_dal.update_capture(capture_id,
                                            annotation=capture.annotation,
                                            date_updated=datetime.now().utcnow().replace(microsecond=0))


@app.delete("/captures/{capture_id}")
async def delete_capture_by_id(capture_id: int,
                               session: AsyncSession = Depends(get_session),
                               _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    return await capture_dal.delete_capture_by_id(capture_id=capture_id)


@app.post("/captures/{capture_id}/add_image")
async def add_image_to_album(image: Image, capture_id: int,
                             session: AsyncSession = Depends(get_session),
                             _api_key: APIKey = Depends(get_api_key)) -> Image:
    if image.date_created is None:
        image.date_created = datetime.now().utcnow().replace(microsecond=0)
    image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id)
    capture.date_updated = datetime.now().utcnow().replace(microsecond=0)
    # https://stackoverflow.com/questions/50026672/sql-alchemy-how-to-insert-data-into-two-tables-and-reference-foreign-key
    await image_dal.create_image(image, capture)
    # await capture_dal.add_to_capture_image_album(image.image_id, capture_id)
    return image


@app.post("/captures/{capture_id}/add_images")
async def add_images_to_album(images: CreateImages, capture_id: int,
                              session: AsyncSession = Depends(get_session),
                              _api_key: APIKey = Depends(get_api_key)):
    image_dal = CaptureImageDAL(session)
    capture_dal = CaptureAlbumDAL(session)
    list_of_images = []
    capture = await capture_dal.get_capture_by_id(capture_id)
    capture.date_updated = datetime.now().utcnow().replace(microsecond=0)
    for i in images.images:
        if i.date_created is None:
            i.date_created = datetime.now().utcnow().replace(microsecond=0)
        capture_image = CaptureImage(encoded=i.encoded, date_created=i.date_created)
        capture_image.image_album.append(capture)
        list_of_images.append(capture_image)

    image_dal.db_session.add_all(list_of_images)
    await image_dal.db_session.commit()
    # await image_dal.db_session.flush()
    return images


@app.delete("/captures/{capture_id}/remove_images")
async def delete_images_from_album(images: DeleteImages, capture_id: int,
                                   session: AsyncSession = Depends(get_session),
                                   _api_key: APIKey = Depends(get_api_key)):
    image_dal = CaptureImageDAL(session)
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id)
    capture.date_updated = datetime.now().utcnow().replace(microsecond=0)
    for i in images.image_ids:
        await image_dal.delete_image(i)


@app.post("/image", response_model=Image)
async def add_image(image: Image,
                    session: AsyncSession = Depends(get_session),
                    _api_key: APIKey = Depends(get_api_key)) -> CaptureImage:
    image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    await image_dal.create_image(image)
    return image


@app.delete("/images/{image_id}")
async def delete_image_by_id(image_id: int,
                             session: AsyncSession = Depends(get_session),
                             _api_key: APIKey = Depends(get_api_key)):
    image_dal = CaptureImageDAL(session)
    return await image_dal.delete_image(image_id)


if __name__ == '__main__':
    # asyncio.run(async_main())
    uvicorn.run("app.server:app", port=1111, host='127.0.0.1', reload=True)
