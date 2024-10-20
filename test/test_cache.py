import pytest
from datetime import datetime
from thames_tidal_helper.Client import Client, Quarter
import os
import shutil
CACHE_TEST_PATH = "test/.cache/"
EXAMPLE_FILE = "test/example_data.json"

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
    quarter = Quarter(2014, 1)
    client.cache.write_to_cache(quarter, data)
    assert client.cache.check_exists(quarter)
    

