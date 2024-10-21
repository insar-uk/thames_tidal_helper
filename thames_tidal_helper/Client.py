import json
import os
from datetime import datetime

import requests as req


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
            raise ValueError(
                f"Site code for {site} not found. Please add it to the API.site_codes dictionary."
            )

        return f"{API.root}{site_code}/{year}/{month}/{day}/0/1/"


class TideEntry:
    def __init__(self, time: datetime, type: str, height: float):
        self.time = time
        self.height = height
        self.type = type

    def __str__(self) -> str:
        return f"{self.time}: {self.type} - {self.height}m"

    def __repr__(self) -> str:
        return self.__str__()


class DataPackage:
    def __init__(self, data: str):
        self.data = data
        self.json_data = json.loads(data)
        self.table = self.json_data["table"]

    def parse(self) -> list[TideEntry]:
        entries = []
        # go through each month in the table
        for _, month_data in self.table.items():
            # get the month and year from 'month['name']' which is in the format 'January 2021'
            month_str, year_str = month_data["name"].split(" ")
            # convert the month to a number
            month = datetime.strptime(month_str, "%B").month
            year = int(year_str)

            # go through each day in the month
            for _, day_data in month_data["rows"].items():
                # go through each entry in the day
                for entry in day_data:
                    day = entry["Day"]
                    hour = int(entry["Time"][:2])
                    minute = int(entry["Time"][2:])
                    # time is in the format '2010' for 10 minutes past 8pm
                    time = datetime(year, month, day, hour, minute)
                    height_str = entry["Height"].replace("m", "")
                    height = float(height_str)
                    type = "LOW" if entry["Type"] == 0 else "HIGH"
                    entries.append(TideEntry(time, type, height))

        return entries


class CalendarQuarter:
    def __init__(self, year: int, quarter: int):
        self.year = year
        self.quarter = quarter

    def __eq__(self, other):
        return self.year == other.year and self.quarter == other.quarter

    def __hash__(self):
        return hash((self.year, self.quarter))

    def __repr__(self):
        return f"{self.year} Q{self.quarter}"


class CacheManager:
    def __init__(self, cache_directory: str = "/.cache/"):
        self.cache_directory = cache_directory
        self.contents: list[CalendarQuarter] = []

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)
        else:
            # load the contents of the cache
            for filename in os.listdir(cache_directory):
                year, quarter = filename.split("_Q")
                quarter = quarter.split(".")[0]
                self.contents.append(CalendarQuarter(int(year), int(quarter)))

    def quarter_to_filename(self, quarter: CalendarQuarter) -> str:
        return f"{quarter.year}_Q{quarter.quarter}.json"

    def check_exists(self, quarter: CalendarQuarter) -> bool:
        filename = self.quarter_to_filename(quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if quarter not in self.contents:
            return False
        if os.path.exists(filepath):
            return True
        else:
            raise FileNotFoundError(
                f"File {filepath} was expected to exist but was not found."
            )

    def get_from_cache(self, quarter: CalendarQuarter) -> DataPackage | None:
        filename = self.quarter_to_filename(quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if quarter not in self.contents:
            return None
        with open(filepath, "r") as file:
            contents = file.read()
            return DataPackage(contents)

    def write_to_cache(self, quarter: CalendarQuarter, data: str):
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


def datetime_to_quarter(dt: datetime) -> CalendarQuarter:
    year = dt.year
    month = dt.month
    quarter = (month - 1) // 3 + 1
    return CalendarQuarter(year, quarter)


def get_quarters_to_query(datetimes: list[datetime]) -> list[CalendarQuarter]:
    # Parse through each date
    quarters = []
    for dt in datetimes:
        quarters.append(datetime_to_quarter(dt))

    # Remove duplicates
    quarters = list(set(quarters))

    return quarters


def quarter_to_month(q: int) -> int:
    return q * 3 - 2


def get_quarters(
    site, quarters: list[CalendarQuarter], cache: CacheManager
) -> list[CalendarQuarter]:
    # for each quarter, first check the cache, then query the API for the 1st day of the quarter
    for quarter in quarters:
        jsonData = cache.check_exists(quarter)
        if jsonData:
            continue
        # Query the API
        response = req.get(
            API.query(site, quarter.year, quarter_to_month(quarter.quarter) * 3 - 2, 1)
        )
        cache.write_to_cache(quarter, response.text)

    return quarters


class Client:
    def __init__(self, cache_path: str = "./.cache/", site: str = "Chelsea Bridge"):
        self.cache = CacheManager(cache_path)
        self.site = site

    def get_entry_list(self, quarters: list[CalendarQuarter]) -> list[TideEntry]:
        entry_list = []
        for quarter in quarters:
            data = self.cache.get_from_cache(quarter)
            if not data:
                raise ValueError(f"Data for {quarter} not found in cache.")
            entries = data.parse()
            assert len(entries) > 0, f"No entries found for {quarter}."
            entry_list.extend(entries)

        return entry_list

    def interpolate_tidal_heights(
        self, entries: list[TideEntry], datetimes: list[datetime]
    ) -> dict[datetime, float]:
        results: dict[datetime, float] = {}
        for dt in datetimes:
            # Find the two closest entries, smaller and greater than the datetime
            sntd = 99999  # some number that's too big
            sptd = 99999
            earlier_tide_point: TideEntry = entries[0]
            later_tide_point: TideEntry = entries[1]
            for entry in entries:
                delta = (dt - entry.time).total_seconds()
                if delta < 0 and abs(delta) < sntd:
                    sntd = abs(delta)
                    earlier_tide_point = entry
                elif delta > 0 and abs(delta) < sptd:
                    sptd = abs(delta)
                    later_tide_point = entry
            # interpolate linearly between the two closest entries
            gradient = (later_tide_point.height - earlier_tide_point.height) / (
                later_tide_point.time - earlier_tide_point.time
            ).total_seconds()
            height = (
                gradient * (dt - earlier_tide_point.time).total_seconds()
                + earlier_tide_point.height
            )

            results[dt] = height
        return results

    def run(self):
        datetimes = self.load_input_datetimes()
        # convert to quarters
        quartersToQuery = get_quarters_to_query(datetimes)
        quarters = get_quarters(self.site, quartersToQuery, self.cache)
        entry_list = self.get_entry_list(quarters)
        results = self.interpolate_tidal_heights(entry_list, datetimes)
        for dt, height in results.items():
            print(f"{dt}, {height}")

        with open("output.txt", "w") as file:
            file.write("Datetime, Tidal Height (m)\n")
            for dt, height in results.items():
                file.write(f"{dt}, {height}\n")

    @staticmethod
    def load_input_datetimes(input_file: str = "input.txt"):
        with open(input_file, "r") as file:
            datetime_strings: list[str] = file.readlines()
            # format is: '2021-02-12T10:01:01.000Z\n'
            datetimes = [
                datetime.strptime(dstr.strip(), "%Y-%m-%dT%H:%M:%S.%fZ")
                for dstr in datetime_strings
            ]
        return datetimes
