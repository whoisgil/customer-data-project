# pytest test cases for the export functions

# importing needed libraries
import csv
import json
import pytest

from functions.export_functions import (
    backupExistingFile,
    writePhoneJson,
    writeLocationCsv,
    writeExportFiles
)


@pytest.fixture
def sample_records():
    """Builds accepted records used by the export tests."""

    return [
        {
            "f_name": "FirstName",
            "l_name": "LastName",
            "county": "County",
            "state": "PA",
            "primary_phone": "555-555-0100",
            "secondary_phone": "555-555-0101"
        },
        {
            "f_name": "Second",
            "l_name": "Person",
            "county": "Other",
            "state": "OH",
            "primary_phone": "555-555-0200",
            "secondary_phone": ""
        }
    ]


# Tests for writing and backing up export files.

def testWritePhoneJsonStructure(tmp_path, sample_records):
    """Tests the fields and structure of the JSON file."""

    output_path = tmp_path / "customer_phone.json"

    assert writePhoneJson(sample_records, str(output_path))

    with open(output_path, encoding="utf-8") as json_file:
        written_data = json.load(json_file)

    assert written_data == [
        {
            "first_name": "FirstName",
            "phone_numbers": [
                "555-555-0100",
                "555-555-0101"
            ]
        },
        {
            "first_name": "Second",
            "phone_numbers": ["555-555-0200"]
        }
    ]


def testWriteLocationCsvStructure(tmp_path, sample_records):
    """Tests the headers and columns of the CSV file."""

    output_path = tmp_path / "customer_location.csv"

    assert writeLocationCsv(sample_records, str(output_path))

    with open(output_path, encoding="utf-8", newline="") as csv_file:
        rows = list(csv.reader(csv_file))

    assert rows[0] == [
        "first_name",
        "last_name",
        "county",
        "state"
    ]

    assert rows[1] == [
        "FirstName",
        "LastName",
        "County",
        "PA"
    ]

    assert rows[2] == [
        "Second",
        "Person",
        "Other",
        "OH"
    ]


def testBackupExistingFileCreatesCopy(tmp_path):
    """Tests that an existing file is backed up."""

    output_path = tmp_path / "customer_phone.json"
    output_path.write_text("old contents", encoding="utf-8")

    assert backupExistingFile(str(output_path))

    backup_path = tmp_path / "customer_phone.json.copy"

    assert backup_path.exists()
    assert backup_path.read_text(encoding="utf-8") == "old contents"


def testWritePhoneJsonBacksUpBeforeOverwrite(
    tmp_path,
    sample_records
):
    """Tests that old JSON contents are backed up."""

    output_path = tmp_path / "customer_phone.json"
    output_path.write_text("old contents", encoding="utf-8")

    writePhoneJson(sample_records, str(output_path))

    backup_path = tmp_path / "customer_phone.json.copy"

    assert backup_path.read_text(
        encoding="utf-8"
    ) == "old contents"


def testWritePhoneJsonHandlesUnwritableDirectory(
    tmp_path,
    sample_records
):
    """Tests that a JSON write failure returns False."""

    bad_path = (
        tmp_path
        / "no_such_directory"
        / "customer_phone.json"
    )

    assert not writePhoneJson(sample_records, str(bad_path))


def testWriteLocationCsvHandlesUnwritableDirectory(
    tmp_path,
    sample_records
):
    """Tests that a CSV write failure returns False."""

    bad_path = (
        tmp_path
        / "no_such_directory"
        / "customer_location.csv"
    )

    assert not writeLocationCsv(sample_records, str(bad_path))


def testWriteExportFilesReturnsBothResults(
    tmp_path,
    sample_records
):
    """Tests that both export results are returned."""

    phone_path = tmp_path / "customer_phone.json"
    location_path = tmp_path / "customer_location.csv"

    phone_written, location_written = writeExportFiles(
        sample_records,
        str(phone_path),
        str(location_path)
    )

    assert phone_written
    assert location_written