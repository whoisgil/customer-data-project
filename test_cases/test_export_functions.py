# unittest test cases for the export functions

# importing needed libraries
import csv
import json
import tempfile
import unittest
from pathlib import Path

from functions.export_functions import (
    backupExistingFile,
    writePhoneJson,
    writeLocationCsv,
    writeExportFiles
)


class TestExportFunctions(unittest.TestCase):

    def setUp(self):
        """Builds a temporary directory and sample records used by the tests."""

        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

        self.sample_records = [
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

    def tearDown(self):
        """Removes the temporary directory."""

        self.temp_dir.cleanup()

    # Tests for writing and backing up export files.

    def testWritePhoneJsonStructure(self):
        """Tests the fields and structure of the JSON file."""

        output_path = self.temp_path / "customer_phone.json"

        self.assertTrue(
            writePhoneJson(
                self.sample_records,
                str(output_path)
            )
        )

        with open(output_path, encoding="utf-8") as json_file:
            written_data = json.load(json_file)

        expected_data = [
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

        self.assertEqual(written_data, expected_data)

    def testWriteLocationCsvStructure(self):
        """Tests the headers and columns of the CSV file."""

        output_path = self.temp_path / "customer_location.csv"

        self.assertTrue(
            writeLocationCsv(
                self.sample_records,
                str(output_path)
            )
        )

        with open(
            output_path,
            encoding="utf-8",
            newline=""
        ) as csv_file:
            rows = list(csv.reader(csv_file))

        self.assertEqual(
            rows[0],
            ["first_name", "last_name", "county", "state"]
        )

        self.assertEqual(
            rows[1],
            ["FirstName", "LastName", "County", "PA"]
        )

        self.assertEqual(
            rows[2],
            ["Second", "Person", "Other", "OH"]
        )

    def testBackupExistingFileCreatesCopy(self):
        """Tests that an existing file is backed up."""

        output_path = self.temp_path / "customer_phone.json"
        output_path.write_text(
            "old contents",
            encoding="utf-8"
        )

        self.assertTrue(
            backupExistingFile(str(output_path))
        )

        backup_path = (
            self.temp_path
            / "customer_phone.json.copy"
        )

        self.assertTrue(backup_path.exists())

        self.assertEqual(
            backup_path.read_text(encoding="utf-8"),
            "old contents"
        )

    def testWritePhoneJsonBacksUpBeforeOverwrite(self):
        """Tests that old JSON contents are backed up."""

        output_path = self.temp_path / "customer_phone.json"
        output_path.write_text(
            "old contents",
            encoding="utf-8"
        )

        writePhoneJson(
            self.sample_records,
            str(output_path)
        )

        backup_path = (
            self.temp_path
            / "customer_phone.json.copy"
        )

        self.assertEqual(
            backup_path.read_text(encoding="utf-8"),
            "old contents"
        )

    def testWritePhoneJsonHandlesUnwritableDirectory(self):
        """Tests that a JSON write failure returns False."""

        bad_path = (
            self.temp_path
            / "no_such_directory"
            / "customer_phone.json"
        )

        self.assertFalse(
            writePhoneJson(
                self.sample_records,
                str(bad_path)
            )
        )

    def testWriteLocationCsvHandlesUnwritableDirectory(self):
        """Tests that a CSV write failure returns False."""

        bad_path = (
            self.temp_path
            / "no_such_directory"
            / "customer_location.csv"
        )

        self.assertFalse(
            writeLocationCsv(
                self.sample_records,
                str(bad_path)
            )
        )

    def testWriteExportFilesReturnsBothResults(self):
        """Tests that both export results are returned."""

        phone_path = self.temp_path / "customer_phone.json"
        location_path = self.temp_path / "customer_location.csv"

        phone_written, location_written = writeExportFiles(
            self.sample_records,
            str(phone_path),
            str(location_path)
        )

        self.assertTrue(phone_written)
        self.assertTrue(location_written)


if __name__ == "__main__":
    unittest.main()