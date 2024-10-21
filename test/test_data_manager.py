import os
import shutil
from unittest.mock import patch

import pytest

from conftest import CACHE_TEST_PATH, EXAMPLE_FILE
from thames_tidal_helper.data_manager import DataManager
from thames_tidal_helper.schema import CalendarQuarter
from thames_tidal_helper.api_adapter import API


@pytest.fixture(scope="module", autouse=True)
def wipe_cache():
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)
    yield
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)


@pytest.fixture(scope="module", autouse=True)
def example_data():
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    yield data


def test_cache_directory(wipe_cache):
    assert not os.path.exists(CACHE_TEST_PATH)
    _ = DataManager(CACHE_TEST_PATH)
    assert os.path.exists(CACHE_TEST_PATH)


def test_generate_filename():
    data_manager = DataManager(CACHE_TEST_PATH)
    site = "Chelsea Bridge"
    quarter = CalendarQuarter(2014, 1)
    filename = data_manager.generate_filename(site, quarter)
    assert API.site_to_code(site) in filename or site in filename
    assert "2014_Q1" in filename

    # Now test with a different site
    site = "Wibble Bridge"
    with pytest.raises(ValueError):
        filename = data_manager.generate_filename(site, quarter)


def test_parse_filename():
    filename = "0113A_2014_Q1.json"
    data_manager = DataManager(CACHE_TEST_PATH)
    site, quarter = data_manager.parse_filename(filename)
    assert site == API.code_to_site("0113A")
    assert quarter == CalendarQuarter(2014, 1)


def test_invalid_filename():
    bad_filename = "wibble_2014_Q1.json"
    with pytest.raises(ValueError):
        data_manager = DataManager(CACHE_TEST_PATH)
        data_manager.parse_filename(bad_filename)

    bad_filename = "0113A_24_Q4.txt"
    with pytest.raises(ValueError):
        data_manager = DataManager(CACHE_TEST_PATH)
        data_manager.parse_filename(bad_filename)


def test_add_data_to_cache(wipe_cache, example_data):
    data_manager = DataManager(CACHE_TEST_PATH)
    site = "Chelsea Bridge"
    # read in the example data from the file
    assert os.path.exists(EXAMPLE_FILE)
    assert example_data is not None

    # add the data to the cache
    quarter = CalendarQuarter(2014, 1)
    data_manager.write_to_cache(site, quarter, example_data)
    assert data_manager.check_exists(site, quarter)

    filepath = os.path.join(
        CACHE_TEST_PATH, data_manager.generate_filename(site, quarter)
    )
    assert os.path.exists(filepath)

    # read the data back from the cache
    cached_data = data_manager.get_from_cache(site, quarter)
    assert cached_data is not None

    # Now delete the file to mess with the cache
    with pytest.raises(FileNotFoundError):
        os.remove(filepath)
        assert not os.path.exists(filepath)
        _ = data_manager.check_exists(site, quarter)


def test_no_entry_in_cache(wipe_cache):
    site = "Chelsea Bridge"
    data_manager = DataManager(CACHE_TEST_PATH)
    quarter = CalendarQuarter(2014, 1)
    assert not data_manager.check_exists(site, quarter)
    assert data_manager.get_from_cache(site, quarter) is None


def test_bad_data(wipe_cache):
    data_manager = DataManager(CACHE_TEST_PATH)
    quarter = CalendarQuarter(2014, 1)
    site = "Chelsea Bridge"
    with pytest.raises(ValueError):
        data_manager.write_to_cache(site, quarter, "bad data")
    assert not data_manager.check_exists(site, quarter)
    assert data_manager.get_from_cache(site, quarter) is None


def test_retrieve_data(wipe_cache, example_data):
    data_manager = DataManager(CACHE_TEST_PATH)
    site = "Chelsea Bridge"
    # Add the example data to the cache
    quarter = CalendarQuarter(2014, 1)
    assert not data_manager.check_exists(site, quarter)
    data_manager.write_to_cache(site, quarter, example_data)
    _ = data_manager.get_quarters("Chelsea Bridge", [quarter])
    # Now check that the data is in the cache
    assert data_manager.check_exists(site, quarter)

    # Now try with a different quarter
    quarter = CalendarQuarter(2024, 1)
    assert not data_manager.check_exists(site, quarter)
    data_manager.get_quarters("Chelsea Bridge", [quarter])
    assert data_manager.check_exists(site, quarter)


def test_wipe_cache(wipe_cache, example_data):
    data_manager = DataManager(CACHE_TEST_PATH)
    site = "Chelsea Bridge"
    # Add the example data to the cache
    quarter = CalendarQuarter(2014, 1)
    data_manager.write_to_cache(site, quarter, example_data)
    assert data_manager.check_exists(site, quarter)

    # Preload user input to bypass the input prompt
    input_values = ["n", "y"]

    def mock_input(s):
        return input_values.pop(0)

    with patch("builtins.input", side_effect=mock_input):
        # First test cancelling the wipe
        data_manager.wipe_cache()  # Should not delete the cache
        assert data_manager.check_exists(site, quarter)

        # Wipe the cache using the method on DataManager
        data_manager.wipe_cache()
        assert not data_manager.check_exists(site, quarter)
        assert data_manager.get_from_cache(site, quarter) is None

    # Manually clean up the cache directory
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)
