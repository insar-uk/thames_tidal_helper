import os
import sys
import subprocess
import pytest
import uuid
from datetime import datetime

from thames_tidal_helper.config import DEFAULT_CACHE_PATH

# Define paths for input and output files
INPUT_FILE = "test_input.txt"
OUTPUT_FILE = "test_output.txt"
DEFAULT_INPUT_FILE = "input.txt"
DEFAULT_OUTPUT_FILE = "output.txt"

CACHE_TEST_PATH = "test/.cache_for_test_commands/"

venv_python = sys.executable


@pytest.fixture(scope="module", autouse=True)
def setup_files():
    unique_str: str = uuid.uuid4().hex[:6].upper()
    nowish = datetime.now().strftime("%Y%m%d%H%M%S")
    suffix = f"{unique_str}.{nowish}.bak"
    # Backup the default input and output files
    if os.path.exists(DEFAULT_INPUT_FILE):
        os.rename(
            DEFAULT_INPUT_FILE, f"{DEFAULT_INPUT_FILE}.{suffix}"
        )  # pragma: no cover
    if os.path.exists(DEFAULT_OUTPUT_FILE):
        os.rename(
            DEFAULT_OUTPUT_FILE, f"{DEFAULT_OUTPUT_FILE}.{suffix}"
        )  # pragma: no cover

    # Create a test input file
    with open(INPUT_FILE, "w") as f:
        f.write("2024-01-01 00:00:00\n2024-02-02 00:00:00\n")

    # Create a test default input file
    with open(DEFAULT_INPUT_FILE, "w") as f:
        f.write("2014-01-01 00:00:00\n2014-01-02 00:00:00\n")

    yield

    # Clean up the test files
    if os.path.exists(INPUT_FILE):
        os.remove(INPUT_FILE)  # pragma: no cover
    if os.path.exists(DEFAULT_INPUT_FILE):
        os.remove(DEFAULT_INPUT_FILE)  # pragma: no cover
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)  # pragma: no cover
    if os.path.exists(DEFAULT_OUTPUT_FILE):
        os.remove(DEFAULT_OUTPUT_FILE)  # pragma: no cover

    # Restore the default input and output files
    if os.path.exists(f"{DEFAULT_INPUT_FILE}.{suffix}"):
        os.rename(
            f"{DEFAULT_INPUT_FILE}.{suffix}", DEFAULT_INPUT_FILE
        )  # pragma: no cover
    if os.path.exists(f"{DEFAULT_OUTPUT_FILE}.{suffix}"):
        os.rename(
            f"{DEFAULT_OUTPUT_FILE}.{suffix}", DEFAULT_OUTPUT_FILE
        )  # pragma: no cover


@pytest.fixture(scope="module", autouse=True)
def preload_cache():
    if not os.path.exists(DEFAULT_CACHE_PATH):
        os.mkdir(DEFAULT_CACHE_PATH)  # pragma: no cover
    if not os.path.exists(CACHE_TEST_PATH):
        os.mkdir(CACHE_TEST_PATH)  # pragma: no cover

    # Copy the example data to the cache
    for file in os.listdir(os.path.join("test", "example_data")):
        old_filepath = os.path.join("test", "example_data", file)
        new_filepath = os.path.join(DEFAULT_CACHE_PATH, file)
        new_test_filepath = os.path.join(CACHE_TEST_PATH, file)

        import shutil

        if not os.path.exists(new_filepath):
            shutil.copyfile(old_filepath, new_filepath)  # pragma: no cover
        if not os.path.exists(new_test_filepath):
            shutil.copyfile(old_filepath, new_test_filepath)  # pragma: no cover

    yield

    # Clean up the cache
    for file in os.listdir(CACHE_TEST_PATH):
        os.remove(os.path.join(CACHE_TEST_PATH, file))
    os.rmdir(CACHE_TEST_PATH)


def test_default_options(setup_files, preload_cache):
    # Run the script with default options
    result = subprocess.run(
        [venv_python, "-m", "thames_tidal_helper"], capture_output=True, text=True
    )
    assert result.returncode == 0
    assert os.path.exists("input.txt")
    assert os.path.exists("output.txt")

    # Verify the output file content
    with open("output.txt", "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        for i, line in enumerate(lines):
            if i == 0:
                assert line.strip() == "Datetime, Tidal Height (m)"
                continue

            parts = line.split(",")
            assert len(parts) == 2
            datetime_str, height_str = parts
            assert float(height_str) >= 0.0
            assert "2014-" in datetime_str


def test_custom_options(setup_files):
    # Run the script with custom options
    result = subprocess.run(
        [
            venv_python,
            "-m",
            "thames_tidal_helper",
            "--input",
            INPUT_FILE,
            "--output",
            OUTPUT_FILE,
            "--site",
            "Chelsea Bridge",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert os.path.exists(INPUT_FILE)
    assert os.path.exists(OUTPUT_FILE)

    # Verify the output file content
    with open(OUTPUT_FILE, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        for i, line in enumerate(lines):
            if i == 0:
                assert line.strip() == "Datetime, Tidal Height (m)"
                continue

            parts = line.split(",")
            assert len(parts) == 2
            datetime_str, height_str = parts
            assert float(height_str) >= 0.0
            assert "2024-" in datetime_str


def test_invalid_site_option(setup_files):
    bad_site_name = "Invalid Site"
    # Run the script with an invalid site option
    result = subprocess.run(
        [
            venv_python,
            "-m",
            "thames_tidal_helper",
            "--input",
            INPUT_FILE,
            "--output",
            OUTPUT_FILE,
            "--site",
            bad_site_name,
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert bad_site_name in result.stderr
    assert "not found" in result.stderr.lower()
