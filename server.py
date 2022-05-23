import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from dals.capture_dal import CaptureAlbumDAL
from db.database import get_session, async_session, init_db
from db.models import CaptureAlbum
from db.schemas import *

# from sqlalchemy.ext.asyncio import async_session

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


# @app.get("/captures", response_model=Captures)
# async def get_all_captures() -> dict[str, List[CaptureAlbum]]:
#     async with async_session() as session:
#         async with session.begin():
#             capture_dal = CaptureAlbumDAL(session)
#             captures = await capture_dal.get_all_captures()
#             return {"captures": captures}


@app.post("/captures")
async def create_capture(capture: Capture, session: AsyncSession = Depends(get_session)):
    capture_dal = CaptureAlbumDAL(session)
    # image = await capture_dal.create_image(base64_img="hello==", date_created=datetime.today())
    # print(image.image_id)
    await capture_dal.create_capture(annotation=capture.annotation, coordinates=capture.coordinates,
                                     date_created=datetime.today(), date_updated=datetime.today())
    # await captures.commit()
    return capture


@app.get("/captures/{capture_id}", response_model=DetailedCapture)
async def get_capture_by_id(capture_id: int) -> dict[str, CaptureAlbum]:
    async with async_session() as session:
        async with session.begin():
            capture_dal = CaptureAlbumDAL(session)
            capture = await capture_dal.get_capture_by_id(capture_id=capture_id)
            return {"capture": capture}


@app.delete("/captures/{capture_id}")
async def delete_capture_by_id(capture_id: int):
    async with async_session() as session:
        async with session.begin():
            capture_dal = CaptureAlbumDAL(session)
            return await capture_dal.delete_capture_by_id(capture_id=capture_id)


@app.put("/captures/{capture_id}")
async def update_capture_by_id(capture_id: int, request: Request):
    async with async_session() as session:
        async with session.begin():
            capture_dal = CaptureAlbumDAL(session)
            annotation = await request.json()
            return await capture_dal.update_capture_annotation(capture_id=capture_id,
                                                               update_annotation=annotation['annotation'])


if __name__ == '__main__':
    # asyncio.run(async_main())
    uvicorn.run("server:app", port=1111, host='127.0.0.1', reload=True)
