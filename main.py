import logging
from urllib.request import Request

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
import asyncio
from starlette.responses import FileResponse
from uvicorn import Config, Server

from models.models import Storage, RequestedCoords, Scrapper, Coords, ViewData

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
app = FastAPI()
storage = Storage()
coords_queue = RequestedCoords()


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    logger.debug("Start request page")
    response = await call_next(request)
    logger.debug("Page generated")
    logger.debug("Handle request")
    return response


@app.on_event("startup")
async def startup():
    scrapper = Scrapper(storage, coords_queue)
    asyncio.create_task(scrapper.run())

@app.get("/get")
async def get_file(x: float, y: float) -> FileResponse:
    coords_queue.coords.append(Coords(x, y))
    view_data = ViewData(storage)
    view_data.create_map(float(x), float(y))
    return FileResponse(view_data.file_path)
