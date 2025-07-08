# https://cakeinsauce.notion.site/Real-estate-price-visualization-d6d43baab1c1466897f5a8ecdf777994


# scrapper - use avito api and add info to db
# mapbuilder - get coods and return map with all
import json
from typing import List, Dict, Any
import requests
from string import Template
import folium
from folium.plugins import HeatMap
import re
from collections import deque, Counter
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
import os
from uvicorn import Config, Server

class Item():
    coords: List = [int]
    price: int = 0
    date: int = 0


class ItemsDB():
    it: Item


'''
https://www.avito.ru/js/1/map/items?categoryId=24&locationId=653240&correctorMode=0&page=1&map=eyJzZWFyY2hBcmVhIjp7ImxhdEJvdHRvbSI6NTkuOTY3NTg1NTQ4NjM0MTYsImxhdFRvcCI6NTkuOTk3MDg0MTMwODAzMDEsImxvbkxlZnQiOjMwLjE4OTg5NTU3NzU2Mjc3MywibG9uUmlnaHQiOjMwLjI0MDAyMDY5OTYzMzA4fSwiem9vbSI6MTR9&params%5B201%5D=1059&params%5B178133%5D=1&verticalCategoryId=1&rootCategoryId=4&localPriority=0&disabledFilters%5Bids%5D%5B0%5D=byTitle&disabledFilters%5Bslugs%5D%5B0%5D=bt&subscription%5Bvisible%5D=true&subscription%5BisShowSavedTooltip%5D=false&subscription%5BisErrorSaved%5D=false&subscription%5BisAuthenticated%5D=false&searchArea%5BlatBottom%5D=59.96758554863416&searchArea%5BlonLeft%5D=30.189895577562773&searchArea%5BlatTop%5D=59.99708413080301&searchArea%5BlonRight%5D=30.24002069963308&viewPort%5Bwidth%5D=584&viewPort%5Bheight%5D=687&limit=10&countAndItemsOnly=1
searchArea%5BlatBottom%5D=59.96758554863416&searchArea%5BlonLeft%5D=30.189895577562773&searchArea%5BlatTop%5D=59.99708413080301&searchArea%5BlonRight%5D=30.24002069963308
59.96758554863416 lb
30.189895577562773
59.99708413080301 rt
30.24002069963308
-0.02949858216
-0.05012512207
http://0.0.0.0:8000/get/?x=59.96758554863416&y=30.189895577562773
'''


class Coords:  # todo create compare
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = float(x)
        self.y = float(y)

class StorageItem:
    coords: Coords
    price: int

class Storage:
    data: Dict[int,StorageItem]
    def __init__(self):
        self.data = {}
    def return_with_filter(self, x_max: float, x_min: float, y_max: float, y_min: float) -> Dict[int,StorageItem]:
        return {
            key: value
            for key, value in self.data.items()  # Iterate through key-value pairs in the dictionary
            if x_min < value["coords"].x < x_max and y_min  < value["coords"].y < y_max
        }


class RequestedCoords:
    coords: List[Coords]

    def get_last(self) -> Coords | list[Any]:
        if self.count():
            return self.coords[-1]
        else:
            return []

    def __init__(self):
        self.coords = []

    def count(self) -> int:
        return len(self.coords)


class Scrapper:
    coords_list: List = []
    avito_url: str = "https://www.avito.ru/js/1/map/items?categoryId=24&locationId=653240&correctorMode=0&page=$page&map=eyJzZWFyY2hBcmVhIjp7ImxhdEJvdHRvbSI6NTkuOTUxMzg3OTE4NjkwMDI0LCJsYXRUb3AiOjYwLjAxMDM4NzY0ODMwNjI2LCJsb25MZWZ0IjozMC4xNzc3Mjc0MTA2NzE1OTQsImxvblJpZ2h0IjozMC4yNzc5Nzc2NTQ4MTIyMDh9LCJ6b29tIjoxM30%3D&params%5B201%5D=1059&params%5B499%5D=5254&params%5B178133%5D=1&verticalCategoryId=1&rootCategoryId=4&localPriority=0&disabledFilters%5Bids%5D%5B0%5D=byTitle&disabledFilters%5Bslugs%5D%5B0%5D=bt&subscription%5Bvisible%5D=true&subscription%5BisShowSavedTooltip%5D=false&subscription%5BisErrorSaved%5D=false&subscription%5BisAuthenticated%5D=false&searchArea%5BlatBottom%5D=$bottom&searchArea%5BlonLeft%5D=$left&searchArea%5BlatTop%5D=$top&searchArea%5BlonRight%5D=$right&viewPort%5Bwidth%5D=584&viewPort%5Bheight%5D=687&limit=10&countAndItemsOnly=1"
    raw_data = {}
    x = 0
    y = 0

    def __init__(self, storage: Storage, requested_coords: RequestedCoords):
        self.storage = storage
        self.requested_coords = requested_coords

    async def run(self):  # todo make it better
        while True:
            if self.requested_coords.count() != 0:
                print(f"start parsing ")
                self.get_realstate_items()
                print("data parsed")
            else:
                print("no data")
            await asyncio.sleep(10)

    def get_realstate_items(self):
        current_position = self.requested_coords.coords.pop()
        template = Template(self.avito_url)
        for i in range(10):
            url = template.substitute(bottom=current_position.x - 0.02949858216,
                                      left=current_position.y - 0.05012512207,
                                      top=current_position.x + 0.02949858216,
                                      right=current_position.y + 0.05012512207,
                                      page=i)
            total_pages = self.make_request(url)
            if total_pages == i:
                break
            # if self.requested_coords.get_last() != current_position:
            #     self.requested_coords.coords.insert(0,current_position)
            #     break

    def make_request(self, url: str):
        data = Dict

        try:  # todo add 4xx 5xx handler and retry
            headers = {
                "Content-Encoding": "zstd",  # Compression format
                "Content-Type": "application/json; charset=utf-8"  # JSON format with UTF-8 character set
            }
            response = requests.get(url, timeout=30, headers=headers)  # Set a timeout of 3 seconds
            data = response.json()
        except requests.exceptions.Timeout:
            print("Request timed out!")

        self.storage.data.update(self.parce_info(data))
        return data["totalCount"]

    def parce_info(self, raw_date: Dict) -> Dict:
        real_state = {}
        for i in raw_date["items"]:
            real_state[i["id"]] = {
                "coords": Coords(i["coords"]["lat"], i["coords"]["lng"]),
                "price": int(re.sub(r"\D", "", i["normalizedPrice"]))
            }
        return real_state


class ViewData:

    def __init__(self, storage: Storage):
        self.storage = storage

    def create_map(self, x: float, y: float):
        city_center = [x, y]
        data_points = []
        print("create map")
        for val in self.storage.return_with_filter(x + 0.02949858216,
                                                   x - 0.02949858216,
                                                   y + 0.05012512207,
                                                   y - 0.05012512207).values():
            data_points.append([val["coords"].x, val["coords"].y, val["price"]])

        # Создаём базовую карту
        m = folium.Map(location=city_center, zoom_start=12)

        # Добавляем тепловую карту
        heat_data = [[point[0], point[1], point[2]] for point in data_points]  # Координаты и интенсивность
        HeatMap(heat_data).add_to(m)
        m.save("heatmap.html")
        print("map created")

# storage = Storage()
# coords_queue = RequestedCoords()




def http_server(storage: Storage, coords_queue: RequestedCoords):

    app = FastAPI()
    @app.get("/get/")
    async def get_file(x: float, y: float):
        print("start request page")
        coords_queue.coords.append(Coords(x,y))
        view_data = ViewData(storage)
        view_data.create_map(x, y)
        print("page generated")
        file_path = f"./heatmap.html"
        print("handle request")
        if os.path.exists(file_path):
            return FileResponse(file_path)
        else:
            raise HTTPException(status_code=404, detail="File not found")

    return app

async def main():
    storage = Storage()
    coords_queue = RequestedCoords()
    scrapper = Scrapper(storage, coords_queue)
    scapper_task = asyncio.create_task(scrapper.run())

    # Ожидаем выполнения FastAPI-сервера

    config = Config(app=http_server(storage,coords_queue), host="0.0.0.0", port=8000, log_level="info")
    server = Server(config)
    server_task = asyncio.create_task(server.serve())

    # Работаем до тех пор, пока работает сервер
    await asyncio.gather(scapper_task, server_task)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
