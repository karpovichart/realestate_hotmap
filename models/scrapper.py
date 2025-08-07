import asyncio
import logging
import re
from typing import List, Dict, Any
import requests

from models.coords import Coords
from models.requestedcoords import RequestedCoords
from models.storage import Storage
from string import Template

from models.storageitems import StorageItem


class Scrapper:
    coords_list: List = []
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

        data = Dict
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

    def __parce_info(self, raw_date: Dict[Any, Any]) -> Dict[int, StorageItem]:
        real_state = {}
        for i in raw_date["items"]:
            real_state[int(i["id"])] = StorageItem(
                Coords(i["coords"]["lat"], i["coords"]["lng"]),
                int(re.sub(r"\D", "", i["normalizedPrice"])),
            )
        return real_state
