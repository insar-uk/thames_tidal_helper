# Thames Tidal Data

This script queries and interpolates (in time) tidal data from the Port of London Authority (PLA) website [seen here](http://tidepredictions.pla.co.uk).

## Installation

You just need the requests library really.

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

Install as follows:

```
pip install -e .
```


## Usage

Run the script as follows:

``` bash
python -m thames_tidal_helper
# with options:
python -m thames_tidal_helper --input input.txt --output output.txt --site "Chelsea Bridge"
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