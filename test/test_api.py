from thames_tidal_helper.api_adapter import API


def test_date_passed_to_api():
    query_url1 = API.query_url("Chelsea Bridge", 2021, 1, 1)
    assert "2021/1/1" in query_url1, "Date should be passed to the API"
    query_url2 = API.query_url("Chelsea Bridge", 2021, 12, 31)
    assert "2021/12/31" in query_url2, "Date should be passed to the API"


def test_bad_site_name():
    silly_name = "Wibble"
    try:
        API.query_url(silly_name, 2021, 1, 1)
    except ValueError as e:
        assert "not found" in str(e).lower(), "Error message should be clear"
        assert silly_name in str(
            e
        ), "Error message should include the offending site name"


def test_bad_site_code():
    silly_code = "Wibble"
    try:
        API.code_to_site(silly_code)
    except ValueError as e:
        assert "not found" in str(e).lower(), "Error message should be clear"
        assert silly_code in str(
            e
        ), "Error message should include the offending site code"
