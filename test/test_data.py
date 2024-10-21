from datetime import datetime
from json import loads as json_loads

import pytest

from conftest import EXAMPLE_FILE
from thames_tidal_helper.schema import (
    DataPackage,
    parse_data_package,
    CalendarQuarter,
    validate_table,
)


@pytest.fixture(scope="module", autouse=True)
def example_data():
    with open(EXAMPLE_FILE, "r") as file:
        data = file.read()
    yield data


def test_entry_print():
    from thames_tidal_helper.schema import TideEntry

    entry = TideEntry(datetime(1999, 1, 1), "HIGH", 5.0)
    assert "m" in entry.__repr__()
    assert "1999" in entry.__repr__()


def test_data_package(example_data):
    data = example_data
    assert data is not None
    dp = DataPackage(data)
    assert dp.data == data


def test_parse(example_data):
    data = example_data
    assert data is not None
    dp = DataPackage(data)
    parsed = parse_data_package(dp)
    assert len(parsed) > 90


def test_calenderquarter_hash():
    list_of_quarters = [CalendarQuarter(2021, 1), CalendarQuarter(2021, 2)]
    assert len(set(list_of_quarters)) == 2
    set_of_quarters = set(list_of_quarters)
    set_of_quarters.add(CalendarQuarter(2021, 1))
    assert len(set_of_quarters) == 2


def test_datapackage_ctor_validates_table():
    with pytest.raises(ValueError):
        DataPackage("""{"table": {}}""")


def test_validate_table(example_data):
    from thames_tidal_helper.schema import validate_table

    assert not validate_table(json_loads('{"data": []}'))

    # load the example data
    data = example_data
    dp = DataPackage(data)
    assert validate_table(dp.table), "Table should be valid"


def test_table_invalid_month_data():
    json_table = """{"2021-01": "invalid_month_data"}"""
    table = json_loads(json_table)
    assert not validate_table(table)


def test_table_missing_name_or_rows():
    json_table_missing_rows = """{"2021-01": {"name": "January 2021"}}"""
    table_missing_rows = json_loads(json_table_missing_rows)
    assert not validate_table(table_missing_rows)

    json_table_missing_name = """{"2021-01": {"rows": {}}}"""
    table_missing_name = json_loads(json_table_missing_name)
    assert not validate_table(table_missing_name)


def test_table_invalid_name_or_rows_type():
    json_table_invalid_name = """{"2021-01": {"name": 123, "rows": {}}}"""
    table_invalid_name = json_loads(json_table_invalid_name)
    assert not validate_table(table_invalid_name)

    json_table_invalid_rows = (
        """{"2021-01": {"name": "January 2021", "rows": "invalid_rows"}}"""
    )
    table_invalid_rows = json_loads(json_table_invalid_rows)
    assert not validate_table(table_invalid_rows)


def test_validate_table_invalid_entries_type():
    json_table_invalid_entries = (
        """{"2021-01": {"name": "January 2021", "rows": {"1": "invalid_entries"}}}"""
    )
    table_invalid_entries = json_loads(json_table_invalid_entries)
    assert not validate_table(table_invalid_entries)


def test_validate_table_invalid_entry_type():
    json_table_invalid_entry = (
        """{"2021-01": {"name": "January 2021", "rows": {"1": ["invalid_entry"]}}}"""
    )
    table_invalid_entry = json_loads(json_table_invalid_entry)
    assert not validate_table(table_invalid_entry)


def test_validate_table_missing_entry_keys():
    json_table_missing_entry_keys = (
        """{"2021-01": {"name": "January 2021", "rows": {"1": [{}]}}}"""
    )
    table_missing_entry_keys = json_loads(json_table_missing_entry_keys)
    assert not validate_table(table_missing_entry_keys)


def test_validate_table_invalid_entry_key_types():
    json_table_invalid_entry_key_types = (
        """{"2021-01": {"name": "January 2021", "rows": {"1": 
        [{"Day": "invalid_day", "Time": 123, "Height": 5.0, 
        "Type": "invalid_type"}]}}}"""
    )
    table_invalid_entry_key_types = json_loads(json_table_invalid_entry_key_types)
    assert not validate_table(table_invalid_entry_key_types)
