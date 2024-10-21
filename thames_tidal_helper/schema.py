from json import loads as load_json
from datetime import datetime
from typing import TypedDict, Self


class TideEntry:
    def __init__(self, time: datetime, type: str, height: float):
        self.time = time
        self.height = height
        self.type = type

    def __str__(self) -> str:
        return f"{self.time}: {self.type} - {self.height}m"

    def __repr__(self) -> str:
        return self.__str__()


class TideEntryDict(TypedDict):
    """Type hints for the PLA data entry format"""

    Day: int
    Time: str  # format '1310' for 10 minutes past 1pm
    Height: str  # format '1.23'
    Type: int  # 0 for low, 1 for high


class MonthData(TypedDict):
    """Type hints for the PLA month data format"""

    name: str
    rows: dict[str, list[TideEntryDict]]


""" Type hint for the PLA table format """
TableType = dict[str, MonthData]


def validate_table(table: TableType) -> bool:
    def validate_month_data(month_data: MonthData) -> bool:
        if not isinstance(month_data, dict):
            return False
        if "name" not in month_data or "rows" not in month_data:
            return False
        if not isinstance(month_data["name"], str) or not isinstance(
            month_data["rows"], dict
        ):
            return False
        for day_key, entries in month_data["rows"].items():
            if not isinstance(entries, list):
                return False
            for entry in entries:
                if not isinstance(entry, dict):
                    return False
                if (
                    "Day" not in entry
                    or "Time" not in entry
                    or "Height" not in entry
                    or "Type" not in entry
                ):
                    return False
                if (
                    not isinstance(entry["Day"], int)
                    or not isinstance(entry["Time"], str)
                    or not isinstance(entry["Height"], str)
                    or not isinstance(entry["Type"], int)
                ):
                    return False
        return True

    if len(table.values()) == 0:
        return False  # table should have at least one month

    for month_data in table.values():
        if not validate_month_data(month_data):
            return False
    return True


class DataPackage:
    def __init__(self, data: str):
        self.data = data
        self.json_data = load_json(data)
        self.table: TableType = self.json_data["table"]

        if not validate_table(self.table):
            raise ValueError("Data is not in the correct format")


def parse_data_package(data_package: DataPackage) -> list[TideEntry]:
    entries = []
    # go through each month in the table
    for _, month_data in data_package.table.items():
        # get the month and year from 'month['name']' which is in the format 'January 2021'
        month_str, year_str = month_data["name"].split(" ")
        # convert the month to a number
        month = datetime.strptime(month_str, "%B").month
        year = int(year_str)

        # go through each day in the month
        for _, day_data in month_data["rows"].items():
            # go through each entry in the day
            for entry in day_data:
                day = int(entry["Day"])
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

    def __eq__(self, other: Self) -> bool:
        return self.year == other.year and self.quarter == other.quarter

    def __hash__(self) -> int:
        return hash((self.year, self.quarter))

    def __repr__(self) -> str:
        return f"{self.year} Q{self.quarter}"

    @staticmethod
    def from_datetime(dt: datetime):
        year = dt.year
        month = dt.month
        quarter = (month - 1) // 3 + 1
        return CalendarQuarter(year, quarter)
