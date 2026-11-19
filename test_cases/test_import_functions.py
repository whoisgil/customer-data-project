# unittest test cases for the import functions

# importing needed libraries
import unittest
from functions.import_functions import *


class TestImportFunctions(unittest.TestCase):

    def setUp(self):
        """Builds the lines and records used by the tests"""

        self.header_line = ("##first_name##\\\\##last_name##\\\\##company_name##\\\\"
                            "##address##\\\\##city##\\\\##county##\\\\##state##\\\\"
                            "##zip##\\\\##phone1##\\\\##phone2##\\\\##email##\\\\####\\\\####")

        self.data_line = ("##FirstName##\\\\##LastName##\\\\##Company##\\\\"
                          "##123 Address St##\\\\##City##\\\\##County##\\\\##PA##\\\\"
                          "##15601##\\\\##555-555-0100##\\\\##555-555-0101##\\\\"
                          "##test@email.com##\\\\####\\\\####")

        self.valid_record = {"f_name": "FirstName",
                             "l_name": "LastName",
                             "company": "Company",
                             "address": "123 Address St",
                             "city": "City",
                             "county": "County",
                             "state": "PA",
                             "zip": "15601",
                             "primary_phone": "555-555-0100",
                             "secondary_phone": "555-555-0101",
                             "email_address": "test@email.com"}

    def testParseLineBuildsRecord(self):
        """Tests that a data line is turned into a complete record"""

        parsed_record = parseLine(self.data_line)
        self.assertEqual(parsed_record, self.valid_record)

    def testParseLineRemovesWrappers(self):
        """Tests that the wrapping characters are stripped from every field"""

        parsed_record = parseLine(self.data_line)

        for current_field in parsed_record:
            self.assertFalse(parsed_record[current_field].startswith("#"))
            self.assertFalse(parsed_record[current_field].endswith("#"))

    def testParseLineRejectsShortLine(self):
        """Tests that a line without enough fields returns an empty record"""

        self.assertEqual(parseLine("##FirstName##\\\\##LastName##"), {})
        self.assertEqual(parseLine(""), {})

    def testCleanRecordTrimsSpaces(self):
        """Tests that extra spaces are removed from every field"""

        messy_record = dict(self.valid_record)
        messy_record["city"] = "   City   "
        messy_record["l_name"] = " LastName "

        cleaned_record = cleanRecord(messy_record)

        self.assertEqual(cleaned_record["city"], "City")
        self.assertEqual(cleaned_record["l_name"], "LastName")

    def testCleanRecordCorrectsState(self):
        """Tests that a state abbreviation is raised to upper case"""

        messy_record = dict(self.valid_record)
        messy_record["state"] = "pa"

        self.assertEqual(cleanRecord(messy_record)["state"], "PA")

    def testCleanRecordLowersEmail(self):
        """Tests that an email address is lowered to match other records"""

        messy_record = dict(self.valid_record)
        messy_record["email_address"] = "TEST@EMAIL.COM"

        self.assertEqual(cleanRecord(messy_record)["email_address"], "test@email.com")

    def testCleaningRepairsRecordThatWouldFail(self):
        """Tests that cleaning saves a record validation would otherwise reject"""

        messy_record = dict(self.valid_record)
        messy_record["state"] = "pa"

        self.assertEqual(validateRecord(messy_record), ["state"])
        self.assertEqual(validateRecord(cleanRecord(messy_record)), [])

    def testBuildRecordListSkipsHeader(self):
        """Tests that the header row is not treated as a customer record."""

        record_list, malformed_lines = buildRecordList([
            self.header_line,
            self.data_line
        ])

        self.assertEqual(len(record_list), 1)
        self.assertEqual(record_list[0]["f_name"], "FirstName")
        self.assertEqual(malformed_lines, [])


    def testBuildRecordListSkipsBlankLines(self):
        """Tests that blank lines are ignored."""

        record_list, malformed_lines = buildRecordList([
            self.header_line,
            self.data_line,
            "",
            "   "
        ])

        self.assertEqual(len(record_list), 1)
        self.assertEqual(malformed_lines, [])


    # Tests for matching duplicate customer records.

    def testFindMatchingKeyMatchesEmail(self):
        """Tests finding a duplicate by email address."""

        existing_records = {0: dict(self.valid_record)}
        candidate = dict(self.valid_record)
        candidate["primary_phone"] = "555-555-9999"

        self.assertEqual(
            findMatchingKey(candidate, existing_records),
            0
        )


    def testFindMatchingKeyMatchesPhone(self):
        """Tests finding a duplicate by primary phone."""

        existing_records = {0: dict(self.valid_record)}
        candidate = dict(self.valid_record)
        candidate["email_address"] = "different@email.com"

        self.assertEqual(
            findMatchingKey(candidate, existing_records),
            0
        )

    def testMergeFillsBlankFields(self):
        """Tests that a blank field is filled from the matching record"""

        first_record = dict(self.valid_record)
        first_record["secondary_phone"] = ""

        second_record = dict(self.valid_record)

        merged_record = mergeRecords(first_record, second_record)

        self.assertEqual(merged_record["secondary_phone"], "555-555-0101")

    def testMergeKeepsLongerFirstName(self):
        """Tests that the longer first name survives a merge"""

        short_name_record = dict(self.valid_record)
        short_name_record["f_name"] = "Dan"

        long_name_record = dict(self.valid_record)
        long_name_record["f_name"] = "Daniel"

        self.assertEqual(mergeRecords(short_name_record, long_name_record)["f_name"], "Daniel")
        self.assertEqual(mergeRecords(long_name_record, short_name_record)["f_name"], "Daniel")

    # Tests for removing duplicate customer records.

    def testRemoveDuplicatesMergesMatchingRecords(self):
        """Tests that records sharing an identifier are merged."""

        first_record = dict(self.valid_record)

        second_record = dict(self.valid_record)
        second_record["email_address"] = "different@email.com"

        unique_records, merge_count = removeDuplicates([
            first_record,
            second_record
        ])

        self.assertEqual(len(unique_records), 1)
        self.assertEqual(merge_count, 1)


    def testRemoveDuplicatesKeepsDifferentPeople(self):
        """Tests that records with different identifiers stay separate."""

        first_record = dict(self.valid_record)

        second_record = dict(self.valid_record)
        second_record["email_address"] = "other@email.com"
        second_record["primary_phone"] = "555-555-9999"

        unique_records, merge_count = removeDuplicates([
            first_record,
            second_record
        ])

        self.assertEqual(len(unique_records), 2)
        self.assertEqual(merge_count, 0)

    def testValidateRecordListSplitsRecords(self):
        """Tests that records are separated into accepted and rejected lists"""

        good_record = dict(self.valid_record)

        bad_record = dict(self.valid_record)
        bad_record["state"] = "ZZ"
        bad_record["email_address"] = "other@email.com"

        accepted, rejected = validateRecordList([good_record, bad_record])

        self.assertEqual(len(accepted), 1)
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0][1], ["state"])

    def testReadDataFileHandlesMissingFile(self):
        """Tests that a file that does not exist returns no lines"""

        self.assertEqual(readDataFile("text_files/no_such_file.txt"), [])

    def testImportDataFileHandlesMissingFile(self):
        """Tests that an import of a missing file returns empty results"""

        accepted, rejected, counts = importDataFile("text_files/no_such_file.txt")

        self.assertEqual(accepted, [])
        self.assertEqual(rejected, [])
        self.assertEqual(counts, {})


if __name__ == "__main__":
    unittest.main()