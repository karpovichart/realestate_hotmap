import logging

import folium
from folium.plugins import HeatMap

from models.storage import Storage


class ViewData:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    def create_map(self, x: float, y: float) -> None:
        city_center = [x, y]
        data_points = []
        logging.info("Creating a map")
        for val in self.storage.return_with_filter(
            x + 0.02949858216, x - 0.02949858216, y + 0.05012512207, y - 0.05012512207
        ).values():
            data_points.append([val.coords.x, val.coords.y, val.price])

        m = folium.Map(location=city_center, zoom_start=12)

        heat_data = [[point[0], point[1], point[2]] for point in data_points]
        HeatMap(heat_data).add_to(m)
        m.save("heatmap.html")
        logging.info("Map is created")
