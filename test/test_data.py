from thames_tidal_helper.Client import DataPackage
from conftest import EXAMPLE_FILE
from datetime import datetime

def test_data_package():
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    assert data is not None
    dp = DataPackage(data)
    assert dp.data == data

def test_parse():
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    assert data is not None
    dp = DataPackage(data)
    parsed = dp.parse()
    print(parsed)
    