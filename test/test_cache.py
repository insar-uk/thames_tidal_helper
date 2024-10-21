import pytest
from datetime import datetime
from thames_tidal_helper.Client import Client, CalendarQuarter
import os
import shutil
import json
from conftest import CACHE_TEST_PATH, EXAMPLE_FILE

@pytest.fixture
def wipe_cache_at_end():
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)
    yield
    shutil.rmtree(CACHE_TEST_PATH, ignore_errors=True)

def test_cache(wipe_cache_at_end):
    assert not os.path.exists(CACHE_TEST_PATH)
    client = Client(cache_path=CACHE_TEST_PATH)
    assert os.path.exists(CACHE_TEST_PATH)

    # read in the example data from the file
    assert os.path.exists(EXAMPLE_FILE)  
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    assert data is not None

    # add the data to the cache
    quarter = CalendarQuarter(2014, 1)
    client.cache.write_to_cache(quarter, data)
    assert client.cache.check_exists(quarter)

    # read the data back from the cache
    cached_data = client.cache.get_from_cache(quarter)
    assert cached_data is not None
    

