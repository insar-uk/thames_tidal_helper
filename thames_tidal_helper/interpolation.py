"""
This module provides functions to interpolate tidal heights between known points.

Currently only linear interpolation is used.
"""

from datetime import datetime

from thames_tidal_helper.schema import TideEntry


def interpolate_tidal_heights(
    entries: list[TideEntry], datetimes: list[datetime]
) -> dict[datetime, float]:
    """Linearly interpolate tidal heights for a list of given datetimes, using a list of known TideEntries (height + datetime)."""
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
