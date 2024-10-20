import pytest
from datetime import datetime
from thames_tidal_helper.Client import (
    Client,
    datetime_to_quarter,
    Quarter,
    get_quarters_to_query,
)
import os


@pytest.fixture
def example_file():
    example_file = "test/example_file.txt"
    example_string = "2021-01-01T12:00:00.000Z\n2021-01-02T12:42:00.000Z\n"
    with open(example_file, "w") as file:
        file.write(example_string)
    assert os.path.exists(example_file)
    yield example_file
    os.remove(example_file)
    assert not os.path.exists(example_file)


def test_read_file(example_file):
    """Read a file with datetimes"""
    example_file = "test/example_file.txt"
    example_string = "2021-01-01T12:00:00.000Z\n2021-01-02T12:42:00.000Z\n"
    with open(example_file, "w") as file:
        file.write(example_string)

    client = Client()
    datetimes = client.load_input_datetimes(example_file)
    assert len(datetimes) == 2, "Two datetimes should be read"
    assert (
        datetimes[0].year == 2021
        and datetimes[0].month == 1
        and datetimes[0].day == 1
        and datetimes[0].hour == 12
    ), "Datetime should match the input"
    assert datetimes[1].minute == 42, "Datetime should match the input"


def test_datetime_to_quarter():
    """Test the datetime to quarter conversion"""
    dt = datetime(2021, 2, 21)
    quarter: Quarter = datetime_to_quarter(dt)
    assert (
        quarter.year == 2021 and quarter.quarter == 1
    ), "Datetime should match the input"


def test_get_quarters_to_query():
    """Test the get_quarters_to_query function"""
    datetimes = [datetime(2021, 2, 21), datetime(2021, 2, 21)]
    quarters = get_quarters_to_query(datetimes)
    assert len(quarters) == 1, "Should be only 1 quarter for both dates"

    datetimes.append(datetime(2021, 1, 21))
    datetimes.append(datetime(2021, 3, 21))
    quarters = get_quarters_to_query(datetimes)
    assert len(quarters) == 1, "Should be only 1 quarter for all dates"

    datetimes.append(datetime(2021, 4, 21))
    quarters = get_quarters_to_query(datetimes)
    assert len(quarters) == 2
