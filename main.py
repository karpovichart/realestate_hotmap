import logging

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

@app.on_event("startup")
async def startup():
    scrapper = Scrapper(storage, coords_queue)
    asyncio.create_task(scrapper.run())

@app.get("/get/")
async def get_file(x: float, y: float) -> FileResponse:
    logger.debug("Start request page")
    coords_queue.coords.append(Coords(x, y))
    view_data = ViewData(storage)
    view_data.create_map(float(x), float(y))
    logger.debug("Page generated")
    logger.debug("Handle request")
    return FileResponse(view_data.file_path)
