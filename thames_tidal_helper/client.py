"""Client module for the Thames Tidal Helper package."""

from datetime import datetime

from thames_tidal_helper.data_manager import DataManager
from thames_tidal_helper.schema import TideEntry, CalendarQuarter, parse_data_package
from thames_tidal_helper.interpolation import interpolate_tidal_heights
from thames_tidal_helper.config import DEFAULT_CACHE_PATH


class Client:
    def __init__(
        self,
        cache_path: str = DEFAULT_CACHE_PATH,
        site: str = "Chelsea Bridge",
        silent: bool = False,
        input_file: str = "input.txt",
        output_file: str = "output.txt",
    ):
        self.cache = DataManager(cache_directory=cache_path)
        self.site = site
        self.entry_list: list[TideEntry] = []
        self.input_file = input_file
        self.output_file = output_file
        self.silent = silent

    def populate_entry_list(self, quarters: list[CalendarQuarter]) -> None:
        for quarter in quarters:
            data = self.cache.get_from_cache(self.site, quarter)
            if not data:
                raise ValueError(f"Data for {quarter} not found in cache.")
            entries = parse_data_package(data)
            assert len(entries) > 0, f"No entries found for {quarter}."
            self.entry_list.extend(entries)

    def print_results(self, results: dict[datetime, float]) -> None:
        for dt, height in results.items():
            print(f"{dt}, {height}")

    def run(self):
        """Parse input, get the DataManager to run any queries, load the data, interpolate tidal heights, print/save results."""
        datetimes = self.load_input_datetimes(self.input_file)
        # convert to quarters, remove duplicates
        quarters_to_query = list(
            set([CalendarQuarter.from_datetime(dt) for dt in datetimes])
        )
        self.cache.get_quarters(self.site, quarters_to_query)
        self.populate_entry_list(quarters_to_query)
        results = interpolate_tidal_heights(self.entry_list, datetimes)

        if not self.silent:
            self.print_results(results)

        with open(self.output_file, "w") as file:
            file.write("Datetime, Tidal Height (m)\n")
            for dt, height in results.items():
                file.write(f"{dt}, {height}\n")

    @staticmethod
    def load_input_datetimes(input_file: str) -> list[datetime]:
        with open(input_file, "r") as file:
            datetime_strings: list[str] = file.readlines()
            # format is: '2021-02-12 10:01:01\n'
            datetimes = [
                datetime.strptime(dstr.strip(), "%Y-%m-%d %H:%M:%S")
                for dstr in datetime_strings
            ]
        return datetimes
