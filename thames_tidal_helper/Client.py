import sys
from datetime import datetime
import requests as req
import json
import os

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
        return 0.0


class Quarter:
    def __init__(self, year: int, quarter: int):
        self.year = year
        self.quarter = quarter

class CacheManager:
    def __init__(self, cache_directory: str = "/.cache/"):
        self.cache_directory = cache_directory
        self.contents: list[Quarter] = []

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)

    def quarter_to_filename(self, quarter: Quarter) -> str:
        return f"{quarter.year}_Q{quarter.quarter}.json"
    
    def check_exists(self, quarter: Quarter) -> bool:
        filename = self.quarter_to_filename(quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if quarter not in self.contents:
            return False
        if os.path.exists(filepath):
            return True
        else:
            raise FileNotFoundError(f"File {filepath} was expected to exist but was not found.")
        

    def get_from_cache(self, quarter: Quarter) -> DataPackage | None:
        filename = self.quarter_to_filename(quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if quarter not in self.contents:
            return None
        with open(filepath, "r") as file:
            contents = file.read()
            return DataPackage(contents)
        
    def write_to_cache(self, quarter: Quarter, data: str):
        filename = self.quarter_to_filename(quarter)
        filepath = os.path.join(self.cache_directory, filename)
        with open(filepath, "w") as file:
            file.write(data)
        self.contents.append(quarter)

    

    def wipe_cache(self):
        for quarter in self.contents:
            filename = self.quarter_to_filename(quarter)
            os.remove(filename)
        self.contents = []



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
        if not datapackage:
            raise ValueError("Data package not found in cache.")
        # interpolate the tidal height for the datetime dt
        height = datapackage.get_tidal_height(dt)
        results[dt] = height

class Client:
    def __init__(self, cache_path: str = "/.cache/", site: str = "Chelsea Bridge"):
        self.cache = CacheManager(cache_path)
        self.site = site

    def run(self):
        datetimes = self.load_input_datetimes()
        interpolate_tidal_heights(datetimes, self.cache)

    @staticmethod
    def load_input_datetimes(input_file: str = "input.txt"):
        with open(input_file, "r") as file:
            datetime_strings: list[str] = file.readlines()
            # format is: '2021-02-12T10:01:01.000Z\n'
            datetimes = [datetime.strptime(dstr.strip(), "%Y-%m-%dT%H:%M:%S.%fZ") for dstr in datetime_strings]
        return datetimes

if __name__ == "__main__":
    print("Hello world")
