from models.requestedcoords import Coords, RequestedCoords


def test_initial_state():
    """Test that RequestedCoords initializes with an empty list."""
    requested_coords = RequestedCoords()
    assert requested_coords.count() == 0
    assert requested_coords.coords == []


def test_count_method():
    """Test the count method functionality."""
    requested_coords = RequestedCoords()

    # Initially empty
    assert requested_coords.count() == 0

    # Add one coordinate
    requested_coords.coords.append(Coords(1, 1))
    assert requested_coords.count() == 1

    # Add two more coordinates
    requested_coords.coords.append(Coords(2, 2))
    requested_coords.coords.append(Coords(3, 3))
    assert requested_coords.count() == 3

    assert requested_coords.get_last() == Coords(3, 3)
    requested_coords.delete_last()
    assert requested_coords.count() == 2


def test_get_last_empty():
    """Test get_last() when the coords list is empty."""
    requested_coords = RequestedCoords()
    assert requested_coords.get_last() == []  # Should return an empty list


def test_get_last_with_coords():
    """Test get_last() when there are coordinates in the list."""
    requested_coords = RequestedCoords()

    coords1 = Coords(1, 1)
    coords2 = Coords(2, 2)
    requested_coords.coords.append(coords1)
    requested_coords.coords.append(coords2)

    assert requested_coords.get_last() == coords2
    assert requested_coords.get_last().x == 2
    assert requested_coords.get_last().y == 2
