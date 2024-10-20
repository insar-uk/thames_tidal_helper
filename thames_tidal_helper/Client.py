import sys
from datetime import datetime
import requests as req
import json

"""
# Thames Tidal Data

This script queries and interpolates (in time) tidal data from the Port of London Authority (PLA) website [seen here](http://tidepredictions.pla.co.uk).

## Installation

You just need the requests library. Whether that necessitates a new virtual environment is up to you!

``` bash (linux)
python -m venv venv
source venv/bin/activate
pip install requests
```

``` powershell (windows)
python -m venv venv
.\venv\Scripts\Activate
pip install requests
```


## Usage

This is currently python script not a module. Run it as follows:

``` bash
python thames_tidal_data.py
```

### Options:

- `--input` (default: `input.txt`)

The input file is a line-separated list of datetimess in the format `YYYY-MM-DDTHH:MM:SSZ`. The script will query and interpolate the tidal data for each of these times.

- `--output` (default: `output.txt`)

The tidal heights will be written to this file in the format `2020-05-02T10:01:01Z 1.23`. Where `1.23` is the tidal height in meters at the queried datetime `2020-05-02T10:01:01Z`.

- `--site` (default: `"Chelsea Bridge"`)

The PLA has numerous tidal monitoring sites along the Thames. This option allows you to specify which site to query. The default is `"Chelsea Bridge"`. See http://tidepredictions.pla.co.uk/ for a list of available sites or check Sites.py as some might not be implemented.

## The endpoint

The endpoint is as follows:

`https://tidepredictions.pla.co.uk/gauge_data/<SITE>/<YEAR>/<MONTH>/<DAY>/0/1/`

Where `<SITE>` is the a code for the monitoring site (e.g. `Chelsea Bridge -> 0113A`), and `<YEAR>`, `<MONTH>`, `<DAY>` are the date of the query specified with trailing zeros e.g. '2020', '05', '02'.

In practice however the enpoint returns a json object containing a table with 3 months of data. So we only bother querying each quarter in the range of dates specified. The responses are cached in the `/.cache` directory and used in leiu of querying the endpoint again.
"""

class API:
    root = "https://tidepredictions.pla.co.uk/gauge_data/"

    site_codes = {
        "Chelsea Bridge": "0113A",
        "Richmond": "0113",
    }

    @staticmethod
    def query(site: str, year: int, month: int, day: int):
        try:
            site_code = API.site_codes[site]
        except KeyError:
            raise ValueError(f"Site code for {site} not found. Please add it to the API.site_codes dictionary.")
        
        return f"{API.root}{site_code}/{year}/{month}/{day}/0/1/"
    
class DataPackage:
    def __init__(self, data: str):
        self.data = data
        self.jsonData = json.loads(data)
        self.table = self.jsonData["table"]


    def get_tidal_height(self, datetime: datetime) -> float:
        # get the two nearest times to the datetime (before and after)
        before =

    def get_tidal_heights(self, datetimes: list[datetime]) -> list[float]:
        pass

class Quarter:
    def __init__(self, year: int, quarter: int):
        self.year = year
        self.quarter = quarter

class CacheManager:
    def __init__(self, cache_directory: str = "/.cache/"):
        self.cache_directory = cache_directory
        self.contents: list[Quarter] = []

    def quarter_to_filename(self, quarter: Quarter) -> str:
        return f"{quarter.year}_Q{quarter.quarter}.json"
    
    def check_exists(self, quarter: Quarter) -> bool:
        filename = self.quarter_to_filename(quarter)
        return filename in self.contents

    def get_from_cache(self, quarter: Quarter) -> DataPackage | None:
        filename = self.quarter_to_filename(quarter)
        if quarter not in self.contents:
            return None
        with open(filename, "r") as file:
            contents = file.read()
            return DataPackage(contents)
        
    def write_to_cache(self, quarter: Quarter, data: str):
        filename = self.quarter_to_filename(quarter)
        with open(filename, "w") as file:
            file.write(data)
        self.contents.append(quarter)

def load_input_datetimes(input_file: str = "input.txt"):
    with open(input_file, "r") as file:
        datetime_strings: list[str] = file.readlines()
        # format is: '2021-02-12T10:01:01.000Z\n'
        datetimes = [datetime.strptime(dstr.strip(), "%Y-%m-%dT%H:%M:%S.%fZ") for dstr in datetime_strings]
    return datetimes

def datetime_to_quarter(dt: datetime) -> Quarter:
    year = dt.year
    month = dt.month
    quarter = (month - 1) // 3 + 1
    return Quarter(year, quarter)

def get_quarters_to_query(datetimes: list[datetime]) -> list[Quarter]:
    # Parse through each date
    quarters = []
    for dt in datetimes:
        quarters.append(datetime_to_quarter(dt))
    
    # Remove duplicates
    quarters = list(set(quarters))

    return quarters

def get_quarters(quarters: list[Quarter], cache: CacheManager) -> list[Quarter]:
    # for each quarter, first check the cache, then query the API for the 1st day of the quarter
    for quarter in quarters:
        jsonData = cache.get_from_cache(quarter)
        if jsonData:
            continue
        # Query the API
        response = req.get(API.query("0113A", quarter.year, quarter.quarter * 3 - 2, 1))
        cache.write_to_cache(quarter, response.text)

    return quarters

def interpolate_tidal_heights(datetimes: list[datetime], cache: CacheManager):
    results: dict[datetime, float] = {}
    
    quarters = get_quarters_to_query(datetimes)
    quarters = get_quarters(quarters, cache)


    # Interpolate the tidal heights
    for dt in datetimes:
        datapackage = cache.get_from_cache(datetime_to_quarter(dt))
        # interpolate the tidal height for the datetime dt
        height = datapackage.get_tidal_height(dt)
        results[dt] = height

if __name__ == "__main__":
    print("Hello world")

    # read in
    datetimes = load_input_datetimes()
    print(datetimes)