

def test_read_file():
    """Read a file with datetimes"""
    example_file = "test/example_file.txt"
    example_string = "2021-01-01T12:00.000Z\n2021-01-02T12:00.000Z\n"
    with open(example_file, "w") as file:
        file.write(example_string)

    datetimes = load_input_datetimes(example_file)