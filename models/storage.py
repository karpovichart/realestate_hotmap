from typing import Dict

from models.storageitems import StorageItem

from models.coords import Coords


class Storage:
    __data: Dict[int, StorageItem]

    def __init__(self) -> None:
        self.__data = {0: StorageItem(Coords(0, 0), 0)}

    def update(self, updated_real_estates: Dict[int, StorageItem]) -> None:
        self.__data.update(updated_real_estates)

    def return_with_filter(
        self, x_max: float, x_min: float, y_max: float, y_min: float
    ) -> Dict[int, StorageItem]:
        return {
            key: value
            for key, value in self.__data.items()  # Iterate through key-value pairs in the dictionary
            if x_min < value.coords.x < x_max and y_min < value.coords.y < y_max
        }
