import pytest
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime
from thames_tidal_helper.client import Client
from thames_tidal_helper.schema import TideEntry, CalendarQuarter


@pytest.fixture
def mock_data_manager():
    with patch("thames_tidal_helper.client.DataManager") as MockDataManager:
        mock_data_manager = MockDataManager.return_value
        yield mock_data_manager


@pytest.fixture
def mock_parse_data_package():
    with patch("thames_tidal_helper.client.parse_data_package") as mock_parse:
        yield mock_parse


@pytest.fixture
def mock_interpolate_tidal_heights():
    with patch(
        "thames_tidal_helper.client.interpolate_tidal_heights"
    ) as mock_interpolate:
        yield mock_interpolate


@pytest.fixture
def client(mock_data_manager):
    return Client(cache_path="./.cache/", site="Chelsea Bridge")


def test_populate_entry_list(client, mock_data_manager, mock_parse_data_package):
    mock_data_manager.get_from_cache.return_value = MagicMock()
    mock_parse_data_package.return_value = [TideEntry(datetime.now(), "HIGH", 5.0)]

    quarters = [CalendarQuarter(2021, 1)]
    client.populate_entry_list(quarters)

    assert len(client.entry_list) == 1
    assert client.entry_list[0].height == 5.0


def test_missing_quarter(client, mock_data_manager):
    mock_data_manager.get_from_cache.return_value = None

    with pytest.raises(ValueError):
        client.populate_entry_list([CalendarQuarter(2021, 1)])


def test_run(
    client, mock_data_manager, mock_parse_data_package, mock_interpolate_tidal_heights
):
    mock_data_manager.get_from_cache.return_value = MagicMock()
    mock_parse_data_package.return_value = [TideEntry(datetime.now(), "HIGH", 5.0)]
    mock_interpolate_tidal_heights.return_value = {datetime.now(): 5.0}

    with patch(
        "thames_tidal_helper.client.Client.load_input_datetimes",
        return_value=[datetime(2021, 1, 1)],
    ):
        client.run()

    assert len(client.entry_list) == 1
    assert client.entry_list[0].height == 5.0


def test_load_input_datetimes():
    with patch("builtins.open", mock_open(read_data="2021-02-12 10:01:01\n")):
        datetimes = Client.load_input_datetimes("input.txt")
        assert datetimes == [datetime(2021, 2, 12, 10, 1, 1)]
