import os
import re

from requests import get as req_get

from thames_tidal_helper.schema import DataPackage, CalendarQuarter
from thames_tidal_helper.api_adapter import API
from thames_tidal_helper.config import DEFAULT_CACHE_PATH


class DataManager:
    def __init__(self, cache_directory: str = DEFAULT_CACHE_PATH):
        self.cache_directory = cache_directory
        self.contents: list[tuple[str, CalendarQuarter]] = []

        if not os.path.exists(cache_directory):
            os.mkdir(cache_directory)
        else:
            # load the contents of the cache
            self.filename_pattern = re.compile(r"^[A-Za-z0-9]{5}_\d{4}_Q[1-4]\.json$")
            for filename in os.listdir(cache_directory):
                # check the filename is in the correct format
                if self.filename_pattern.match(filename):
                    site, calender_quarter = self.parse_filename(filename)
                    self.contents.append((site, calender_quarter))

    def check_exists(self, site: str, quarter: CalendarQuarter) -> bool:
        filename = self.generate_filename(site, quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if (site, quarter) not in self.contents:
            return False
        if os.path.exists(filepath):
            return True
        else:
            raise FileNotFoundError(
                f"File {filepath} was expected to exist but was not found."
            )

    def get_from_cache(self, site: str, quarter: CalendarQuarter) -> DataPackage | None:
        filename = self.generate_filename(site, quarter)
        filepath = os.path.join(self.cache_directory, filename)
        if (site, quarter) not in self.contents:
            return None
        with open(filepath, "r") as file:
            contents = file.read()
            return DataPackage(contents)

    def write_to_cache(self, site: str, quarter: CalendarQuarter, data: str):
        filename = self.generate_filename(site, quarter)
        filepath = os.path.join(self.cache_directory, filename)
        # Call the DataPackage constructor to validate the data
        try:
            DataPackage(data)
        except ValueError as e:
            raise ValueError(f"Data is not in the correct format: {e}")

        with open(filepath, "w") as file:
            file.write(data)
        self.contents.append((site, quarter))

    def wipe_cache(self):
        msg = f"Are you sure you want to delete the cache at {self.cache_directory}? (y/n) "
        response = input(msg)
        if response.lower() != "y" and response.lower() != "yes":
            return
        self.contents = []
        for filename in os.listdir(self.cache_directory):
            os.remove(os.path.join(self.cache_directory, filename))
        os.rmdir(self.cache_directory)

    def get_quarters(self, site: str, quarters: list[CalendarQuarter]) -> None:
        # for each quarter, first check the cache, then query the API for the 1st day of the quarter
        def quarter_to_month(q: int) -> int:
            return q * 3 - 2

        for quarter in quarters:
            if self.check_exists(site, quarter):
                continue
            # Query the API
            url = API.query_url(
                site, quarter.year, quarter_to_month(quarter.quarter) * 3 - 2, 1
            )
            response = req_get(url)
            self.write_to_cache(site, quarter, response.text)

    @staticmethod
    def generate_filename(site: str, quarter: CalendarQuarter) -> str:
        try:
            site_code = API.site_to_code(site)
        except ValueError as e:
            raise ValueError(f"Invalid site: {e}")
        return f"{site_code}_{quarter.year}_Q{quarter.quarter}.json"

    @staticmethod
    def parse_filename(filename: str) -> tuple[str, CalendarQuarter]:
        filename.replace(".json", "")
        site_code, year, quarter = filename.split("_")
        year = int(year)
        quarter = int(quarter[1])

        if year < 1900 or quarter < 1 or quarter > 4:
            raise ValueError(f"Invalid year or quarter: {year}, {quarter}")

        # Ctor will raise an exception if the site code is invalid
        site = API.code_to_site(site_code)

        return site, CalendarQuarter(year, quarter)
