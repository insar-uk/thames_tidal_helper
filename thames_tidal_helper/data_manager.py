import os

from requests import get as req_get

from thames_tidal_helper.schema import DataPackage, CalendarQuarter
from thames_tidal_helper.api_adapter import API


class DataManager:
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
        # Call the DataPackage constructor to validate the data
        try:
            DataPackage(data)
        except ValueError as e:
            raise ValueError(f"Data is not in the correct format: {e}")

        with open(filepath, "w") as file:
            file.write(data)
        self.contents.append(quarter)

    def wipe_cache(self):
        msg = f"Are you sure you want to delete the cache at {self.cache_directory}? (y/n) "
        response = input(msg)
        if response.lower() != "y" and response.lower() != "yes":
            return
        self.contents = []
        os.rmdir(self.cache_directory)

    def get_quarters(self, site, quarters: list[CalendarQuarter]) -> None:
        # for each quarter, first check the cache, then query the API for the 1st day of the quarter
        def quarter_to_month(q: int) -> int:
            return q * 3 - 2

        for quarter in quarters:
            json_data = self.check_exists(quarter)
            if json_data:
                continue
            # Query the API
            response = req_get(
                API.query_url(
                    site, quarter.year, quarter_to_month(quarter.quarter) * 3 - 2, 1
                )
            )
            self.write_to_cache(quarter, response.text)
