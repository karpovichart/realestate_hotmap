import logging

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from uvicorn import Config, Server

from models.coords import Coords
from models.requestedcoords import RequestedCoords
from models.scrapper import Scrapper
from models.storage import Storage
from models.viewdata import ViewData

"""
https://www.avito.ru/js/1/map/items?categoryId=24&locationId=653240&correctorMode=0&page=1&map=eyJzZWFyY2hBcmVhIjp7ImxhdEJvdHRvbSI6NTkuOTY3NTg1NTQ4NjM0MTYsImxhdFRvcCI6NTkuOTk3MDg0MTMwODAzMDEsImxvbkxlZnQiOjMwLjE4OTg5NTU3NzU2Mjc3MywibG9uUmlnaHQiOjMwLjI0MDAyMDY5OTYzMzA4fSwiem9vbSI6MTR9&params%5B201%5D=1059&params%5B178133%5D=1&verticalCategoryId=1&rootCategoryId=4&localPriority=0&disabledFilters%5Bids%5D%5B0%5D=byTitle&disabledFilters%5Bslugs%5D%5B0%5D=bt&subscription%5Bvisible%5D=true&subscription%5BisShowSavedTooltip%5D=false&subscription%5BisErrorSaved%5D=false&subscription%5BisAuthenticated%5D=false&searchArea%5BlatBottom%5D=59.96758554863416&searchArea%5BlonLeft%5D=30.189895577562773&searchArea%5BlatTop%5D=59.99708413080301&searchArea%5BlonRight%5D=30.24002069963308&viewPort%5Bwidth%5D=584&viewPort%5Bheight%5D=687&limit=10&countAndItemsOnly=1
searchArea%5BlatBottom%5D=59.96758554863416&searchArea%5BlonLeft%5D=30.189895577562773&searchArea%5BlatTop%5D=59.99708413080301&searchArea%5BlonRight%5D=30.24002069963308
59.96758554863416 lb
30.189895577562773
59.99708413080301 rt
30.24002069963308
-0.02949858216
-0.05012512207
http://0.0.0.0:8000/get/?x=59.96758554863416&y=30.189895577562773

task
https://cakeinsauce.notion.site/Real-estate-price-visualization-d6d43baab1c1466897f5a8ecdf777994
"""


# storage = Storage()
# coords_queue = RequestedCoords()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def http_server(storage: Storage, coords_queue: RequestedCoords) -> FastAPI:
    app = FastAPI()

    @app.get("/get/")
    async def get_file(x: float, y: float) -> FastAPI:
        logger.info("Start request page")
        coords_queue.coords.append(Coords(x, y))
        view_data = ViewData(storage)
        view_data.create_map(x, y)
        logger.info("Page generated")
        file_path = "./heatmap.html"
        logger.info("Handle request")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    return app


async def main() -> None:
    storage = Storage()
    coords_queue = RequestedCoords()
    scrapper = Scrapper(storage, coords_queue)
    scapper_task = asyncio.create_task(scrapper.run())

    config = Config(
        app=http_server(storage, coords_queue),
        host="0.0.0.0",
        port=8000,
        log_level="info",
    )
    server = Server(config)
    server_task = asyncio.create_task(server.serve())

    await asyncio.gather(scapper_task, server_task)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
