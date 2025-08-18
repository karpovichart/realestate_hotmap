import asyncio
import logging
from dataclasses import dataclass
import requests
import folium
from folium.plugins import HeatMap

from string import Template
import re


@dataclass
class Coords:
    x: float
    y: float


@dataclass
class StorageItem:
    coords: Coords
    price: int


class Storage:
    __data: dict[int, StorageItem]

    def __init__(self) -> None:
        self.__data = {0: StorageItem(Coords(0, 0), 0)}

    def update(self, updated_real_estates: dict[int, StorageItem]) -> None:
        self.__data.update(updated_real_estates)

    def return_with_filter(
            self, x_max: float, x_min: float, y_max: float, y_min: float
    ) -> dict[int, StorageItem]:
        return {
            key: value
            for key, value in self.__data.items()
            if float(x_min) < float(value.coords.x) < float(x_max) and float(y_min) < float(value.coords.y) < float(y_max) #todo fix some data is string, cant compare with float
        }


class RequestedCoords:
    coords: list[Coords]

    def __init__(self) -> None:
        self.coords = []

    def get_last(self) -> Coords | list[any]:
        if self.count():
            return self.coords[-1]
        else:
            return []

    def delete_last(self) -> None:
        if self.count():
            self.coords.pop()

    def count(self) -> int:
        return len(self.coords)


class ViewData:
    file_path = "heatmap.html"

    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def create_map(self, x: float, y: float) -> None:
        city_center = [x, y]
        data_points = []
        logging.debug("Creating a map")
        for val in self.storage.return_with_filter(
                x + 0.02949858216, x - 0.02949858216, y + 0.05012512207, y - 0.05012512207
        ).values():
            data_points.append([val.coords.x, val.coords.y, val.price])

        m = folium.Map(location=city_center, zoom_start=12)

        heat_data = [[point[0], point[1], point[2]] for point in data_points]
        HeatMap(heat_data).add_to(m)
        m.save(self.file_path)
        logging.debug("Map is created")


class Scrapper:
    coords_list: list = []
    avito_url: str = (
        "https://www.avito.ru/js/1/map/items?categoryId=24&locationId=653240&correctorMode=0&page=$page"
        "&map=eyJzZWFyY2hBcmVhIjp7ImxhdEJvdHRvbSI6NTkuOTUxMzg3OTE4NjkwMDI0LCJsYXRUb3AiOjYwLjAxMDM4NzY0ODM"
        "wNjI2LCJsb25MZWZ0IjozMC4xNzc3Mjc0MTA2NzE1OTQsImxvblJpZ2h0IjozMC4yNzc5Nzc2NTQ4MTIyMDh9LCJ6b29tIjoxM30%3D"
        "&params%5B201%5D=1059&params%5B499%5D=5254&params%5B178133%5D=1&verticalCategoryId=1&rootCategoryId=4"
        "&localPriority=0&disabledFilters%5Bids%5D%5B0%5D=byTitle&disabledFilters%5Bslugs%5D%5B0%5D=bt"
        "&subscription%5Bvisible%5D=true&subscription%5BisShowSavedTooltip%5D=false"
        "&subscription%5BisErrorSaved%5D=false"
        "&subscription%5BisAuthenticated%5D=false&searchArea%5BlatBottom%5D=$bottom"
        "&searchArea%5BlonLeft%5D=$left&searchArea%5BlatTop%5D=$top&searchArea%5BlonRight%5D=$right"
        "&viewPort%5Bwidth%5D=584&viewPort%5Bheight%5D=687&limit=10&countAndItemsOnly=1"
    )
    raw_data = {}
    x = 0
    y = 0

    def __init__(self, storage: Storage, requested_coords: RequestedCoords) -> None:
        self.storage = storage
        self.requested_coords = requested_coords

    async def run(self) -> None:  # todo make it better
        while True:
            if self.requested_coords.count() != 0:
                logging.info("Start parsing the data")
                self.__get_real_estate_items()
                logging.info("Data is parsed")
            else:
                logging.info("No new data")
            await asyncio.sleep(10)

    def __get_real_estate_items(self) -> None:
        current_position = self.requested_coords.coords.pop()
        template = Template(self.avito_url)
        for i in range(10):
            url = template.substitute(
                bottom=current_position.x - 0.02949858216,
                left=current_position.y - 0.05012512207,
                top=current_position.x + 0.02949858216,
                right=current_position.y + 0.05012512207,
                page=i,
            )
            total_pages = self.__make_request(url)
            if total_pages == i:
                break

    def __make_request(self, url: str) -> int:

        data = dict
        total_count = int
        try:  # todo add 4xx 5xx handler and retry
            headers = {
                "Content-Encoding": "zstd",
                "Content-Type": "application/json; charset=utf-8",
            }
            response = requests.get(url, timeout=30, headers=headers)
            data = response.json()
            total_count = int(data["totalCount"])
        except requests.exceptions.Timeout:
            logging.error("Request timed out")

        self.storage.update(self.__parce_info(data))
        return total_count

    def __parce_info(self, raw_date: dict[any, any]) -> dict[int, StorageItem]:
        real_state = {}
        for i in raw_date["items"]:
            real_state[int(i["id"])] = StorageItem(
                Coords(i["coords"]["lat"], i["coords"]["lng"]),
                int(re.sub(r"\D", "", i["normalizedPrice"])),
            )
        return real_state
