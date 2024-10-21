"""Module to interact with the PLA Tidal Predictions API"""


class API:
    root = "https://tidepredictions.pla.co.uk/gauge_data/"

    class TidalGauge:
        def __init__(self, name: str, code: str):
            self.name = name
            self.code = code

    TIDAL_GAUGES = {
        TidalGauge("Margate", "0103"),
        TidalGauge("Southend", "0110"),
        TidalGauge("Coryton", "0110A"),
        TidalGauge("Tilbury", "0111"),
        TidalGauge("North Woolwich", "0112"),
        TidalGauge("London Bridge", "0113"),
        TidalGauge("Chelsea Bridge", "0113A"),
        TidalGauge("Richmond", "0116"),
        TidalGauge("Shivering Sand", "0116A"),
        TidalGauge("Walton on the Naze", "0129"),
    }

    @staticmethod
    def site_to_code(site: str) -> str:
        """Return the site code for a named site"""
        try:
            gauge = next(gauge for gauge in API.TIDAL_GAUGES if gauge.name == site)
            return gauge.code
        except StopIteration:
            raise ValueError(
                f"Site code for {site} not found. Please add it to the API.SITES list."
            )

    @staticmethod
    def code_to_site(code: str) -> str:
        """Return the site name for a site code"""
        try:
            gauge = next(gauge for gauge in API.TIDAL_GAUGES if gauge.code == code)
            return gauge.name
        except StopIteration:
            raise ValueError(
                f"Site name for {code} not found. Please add it to the API.SITES list."
            )

    @staticmethod
    def query_url(site: str, year: int, month: int, day: int):
        """Return the URL to query the API for a specific date and named site"""
        site_code = API.site_to_code(site)
        return f"{API.root}{site_code}/{year}/{month}/{day}/0/1/"
