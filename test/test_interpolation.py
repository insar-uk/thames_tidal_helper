from datetime import datetime, timedelta

from thames_tidal_helper.interpolation import interpolate_tidal_heights
from thames_tidal_helper.schema import TideEntry


def test_interpolate_tidal_heights():
    data_1 = TideEntry(datetime(2021, 1, 1), "HIGH", 5.0)
    data_2 = TideEntry(datetime(2021, 1, 3), "LOW", 0)

    data = [data_1, data_2]

    query_1 = datetime(2021, 1, 1)
    result_1 = interpolate_tidal_heights(data, [query_1])
    assert result_1[query_1] == 5.0

    query_2 = datetime(2021, 1, 2)
    result_2 = interpolate_tidal_heights(data, [query_2])
    assert result_2[query_2] == 2.5

    query_3 = datetime(2021, 1, 3)
    result_3 = interpolate_tidal_heights(data, [query_3])
    assert result_3[query_3] == 0


def test_many_data_points():
    data = []
    START = datetime(2010, 1, 1)
    for i in range(1, 5000):
        data.append(TideEntry(START + timedelta(hours=i), "HIGH", i))

    query = START + timedelta(hours=4242.5)
    result = interpolate_tidal_heights(data, [query])
    assert result[query] == 4242.5
