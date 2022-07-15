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


async def get_api_key(_api_key_header: str = Security(api_key_header)):
    if _api_key_header == API_KEY:
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


@app.post("/capture", response_model=Capture)
async def create_capture(capture: CreateAndUpdateCapture, session: AsyncSession = Depends(get_session),
                         _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    # https://stackoverflow.com/questions/2150739/iso-time-iso-8601-in-python
    capture.date_created = datetime.now().utcnow().replace(microsecond=0)
    posted_capture = await capture_dal.create_capture(capture)
    if capture.images is not None:
        image_dal = CaptureImageDAL(session)
        _capture = await capture_dal.get_capture_by_id(posted_capture.capture_id)
        list_of_images = []
        for i in capture.images:
            capture_image = CaptureImage(encoded=i.encoded, date_created=i.date_created)
            capture_image.capture_album.append(_capture)
            list_of_images.append(capture_image)
        image_dal.db_session.add_all(list_of_images)
        await image_dal.db_session.commit()
        await image_dal.db_session.flush()
        return _capture
    else:
        return posted_capture


@app.get("/captures/{capture_id}", response_model=Capture)
async def get_capture_by_id(capture_id: int, session: AsyncSession = Depends(get_session),
                            _api_key: APIKey = Depends(get_api_key)) -> dict[str, CaptureAlbum]:
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id=capture_id)
    if capture is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if capture.date_updated is not None:
        capture.date_updated = capture.date_updated.replace(microsecond=0)
    return capture


@app.patch("/captures/{capture_id}", response_model=Capture)
async def update_capture_by_id(capture: CreateAndUpdateCapture, capture_id: int,
                               session: AsyncSession = Depends(get_session),
                               _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    await capture_dal.update_capture(capture_id,
                                     annotation=capture.annotation,
                                     date_updated=datetime.now().utcnow().replace(microsecond=0))
    _capture = await capture_dal.get_capture_by_id(capture_id=capture_id)
    return _capture


@app.delete("/captures/{capture_id}")
async def delete_capture_by_id(capture_id: int,
                               session: AsyncSession = Depends(get_session),
                               _api_key: APIKey = Depends(get_api_key)):
    capture_dal = CaptureAlbumDAL(session)
    await capture_dal.delete_capture_by_id(capture_id=capture_id)
    return


@app.post("/captures/{capture_id}/add_image", response_model=CreateImage)
async def add_image_to_album(image: Image, capture_id: int,
                             session: AsyncSession = Depends(get_session),
                             _api_key: APIKey = Depends(get_api_key)) -> Image:
    if image.date_created is None:
        image.date_created = datetime.now().utcnow().replace(microsecond=0)
    _image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    capture_dal = CaptureAlbumDAL(session)
    capture = await capture_dal.get_capture_by_id(capture_id)
    capture.date_updated = datetime.now().utcnow().replace(microsecond=0)
    # https://stackoverflow.com/questions/50026672/sql-alchemy-how-to-insert-data-into-two-tables-and-reference-foreign-key
    await image_dal.create_image(_image, capture)
    # await capture_dal.add_to_capture_image_album(image.image_id, capture_id)
    return _image


@app.post("/captures/{capture_id}/add_images", response_model=Images,
          response_model_exclude={'images': {'__all__': {'capture_id'}}})
async def add_images_to_album(images: CreateImages, capture_id: int,
                              session: AsyncSession = Depends(get_session),
                              _api_key: APIKey = Depends(get_api_key)) -> dict[str, List[Image]]:

    image_dal = CaptureImageDAL(session)
    capture_dal = CaptureAlbumDAL(session)
    list_of_capture_images = []
    capture = await capture_dal.get_capture_by_id(capture_id)
    capture.date_updated = datetime.now().utcnow().replace(microsecond=0)
    for i in images.images:
        if i.date_created is None:
            i.date_created = datetime.now().utcnow().replace(microsecond=0)
        capture_image = CaptureImage(encoded=i.encoded, date_created=i.date_created)
        capture_image.capture_album.append(capture)
        list_of_capture_images.append(capture_image)

    image_dal.db_session.add_all(list_of_capture_images)
    await image_dal.db_session.commit()
    await image_dal.db_session.flush()
    list_of_images = []
    for n in list_of_capture_images:
        capture_image = Image(encoded=n.encoded, date_created=n.date_created, image_id=n.image_id)
        list_of_images.append(capture_image)

    return {"images": list_of_images}


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
    await image_dal.db_session.commit()


@app.post("/image", response_model=Image)
async def add_image(image: CreateImage,
                    session: AsyncSession = Depends(get_session),
                    _api_key: APIKey = Depends(get_api_key)) -> Image:
    _image = CaptureImage(encoded=image.encoded, date_created=image.date_created)
    image_dal = CaptureImageDAL(session)
    if image.capture_id is None:
        raise HTTPException(status_code=401, detail="Capture ID is required")
    capture_dal = CaptureAlbumDAL(session)
    capture_album = await capture_dal.get_capture_by_id(image.capture_id)
    await image_dal.create_image(_image, capture_album=capture_album)
    return _image


@app.delete("/images/{image_id}")
async def delete_image_by_id(image_id: int,
                             session: AsyncSession = Depends(get_session),
                             _api_key: APIKey = Depends(get_api_key)):
    image_dal = CaptureImageDAL(session)
    await image_dal.delete_image(image_id)
    return


if __name__ == '__main__':
    # asyncio.run(async_main())
    uvicorn.run("app.server:app", port=1111, host='127.0.0.1', reload=True)
