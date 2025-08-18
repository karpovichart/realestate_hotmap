import pytest

from models.models import StorageItem, Coords, Storage


def test_initial_data():
    """Test that the storage initializes with the default data."""
    from models.models import Storage
    storage = Storage()
    data = {
        1: StorageItem(Coords(2, 2), 3),
        2: StorageItem(Coords(20, 20), 3),
        3: StorageItem(Coords(30, 30), 3),
    }
    storage.update(data)
    assert storage.return_with_filter(
        x_min=float(3), x_max=float(23), y_min=float(3), y_max=float(23)
    ) == {2: StorageItem(Coords(20, 20), 3)}


def test_return_with_filter_empty_result():
    """Test that `return_with_filter` returns an empty result when no items match."""
    storage = Storage()
    storage.update(
        {
            1: StorageItem(Coords(5, 5), 1),
            2: StorageItem(Coords(10, 10), 2),
        }
    )

    # Filter with bounds that exclude all items
    result = storage.return_with_filter(x_max=4, x_min=1, y_max=4, y_min=1)
    assert result == {}  # No items should match


def test_return_with_filter_some_matching_items():
    """Test that `return_with_filter` returns only matching items."""
    storage = Storage()
    storage.update(
        {
            1: StorageItem(Coords(3, 3), 1),
            2: StorageItem(Coords(8, 8), 2),
            3: StorageItem(Coords(-1, -1), 3),
        }
    )

    # Filter with bounds that include some items
    result = storage.return_with_filter(x_max=5, x_min=2, y_max=5, y_min=2)

    assert len(result) == 1
    assert 1 in result
    assert result[1].coords.x == 3
    assert result[1].coords.y == 3


def test_return_with_filter_all_matching_items():
    """Test that `return_with_filter` returns all items when they all match."""
    storage = Storage()
    storage.update(
        {
            1: StorageItem(Coords(3, 3), 1),
            2: StorageItem(Coords(4, 4), 2),
        }
    )

    # Filter with bounds that include all items
    result = storage.return_with_filter(x_max=10, x_min=0, y_max=10, y_min=0)

    assert len(result) == 2
