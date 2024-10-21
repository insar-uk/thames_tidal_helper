import os
import shutil

import pytest

from conftest import CACHE_TEST_PATH, EXAMPLE_FILE
from thames_tidal_helper.data_manager import DataManager
from thames_tidal_helper.schema import CalendarQuarter


@pytest.fixture
def wipe_cache_at_end():
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)
    yield
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)


def test_cache(wipe_cache_at_end):
    assert not os.path.exists(CACHE_TEST_PATH)
    data_manager = DataManager(CACHE_TEST_PATH)
    assert os.path.exists(CACHE_TEST_PATH)

    # read in the example data from the file
    assert os.path.exists(EXAMPLE_FILE)
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    assert data is not None

    # add the data to the cache
    quarter = CalendarQuarter(2014, 1)
    data_manager.write_to_cache(quarter, data)
    assert data_manager.check_exists(quarter)

    # read the data back from the cache
    cached_data = data_manager.get_from_cache(quarter)
    assert cached_data is not None
