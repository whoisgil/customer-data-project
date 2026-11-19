# pytest test cases for the import functions

# importing needed libraries
import pytest
from functions.import_functions import *


@pytest.fixture
def header_line():
    """Builds a header line matching the format of the data file"""

    return ("##first_name##\\\\##last_name##\\\\##company_name##\\\\"
            "##address##\\\\##city##\\\\##county##\\\\##state##\\\\"
            "##zip##\\\\##phone1##\\\\##phone2##\\\\##email##\\\\####\\\\####")


@pytest.fixture
def data_line():
    """Builds a data line matching the format of the data file"""

    return ("##FirstName##\\\\##LastName##\\\\##Company##\\\\"
            "##123 Address St##\\\\##City##\\\\##County##\\\\##PA##\\\\"
            "##15601##\\\\##555-555-0100##\\\\##555-555-0101##\\\\"
            "##test@email.com##\\\\####\\\\####")


@pytest.fixture
def valid_record():
    """Builds a valid record used by the tests"""

    return {"f_name": "FirstName",
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


def testParseLineBuildsRecord(data_line, valid_record):
    """Tests that a data line is turned into a complete record"""

    assert parseLine(data_line) == valid_record


def testParseLineRemovesWrappers(data_line):
    """Tests that the wrapping characters are stripped from every field"""

    parsed_record = parseLine(data_line)

    for current_field in parsed_record:
        assert parsed_record[current_field].startswith("#") == False
        assert parsed_record[current_field].endswith("#") == False


def testParseLineRejectsShortLine():
    """Tests that a line without enough fields returns an empty record"""

    assert parseLine("##FirstName##\\\\##LastName##") == {}
    assert parseLine("") == {}


def testCleanRecordTrimsSpaces(valid_record):
    """Tests that extra spaces are removed from every field"""

    valid_record["city"] = "   City   "
    valid_record["l_name"] = " LastName "

    cleaned_record = cleanRecord(valid_record)

    assert cleaned_record["city"] == "City"
    assert cleaned_record["l_name"] == "LastName"


def testCleanRecordCorrectsState(valid_record):
    """Tests that a state abbreviation is raised to upper case"""

    valid_record["state"] = "pa"

    assert cleanRecord(valid_record)["state"] == "PA"


def testCleanRecordLowersEmail(valid_record):
    """Tests that an email address is lowered to match other records"""

    valid_record["email_address"] = "TEST@EMAIL.COM"

    assert cleanRecord(valid_record)["email_address"] == "test@email.com"


def testCleaningRepairsRecordThatWouldFail(valid_record):
    """Tests that cleaning saves a record validation would otherwise reject"""

    valid_record["state"] = "pa"

    assert validateRecord(valid_record) == ["state"]
    assert validateRecord(cleanRecord(valid_record)) == []


# Tests for building imported record lists.

def testBuildRecordListSkipsHeader(header_line, data_line):
    """Tests that the header row is not treated as a customer record."""

    record_list, malformed_lines = buildRecordList([
        header_line,
        data_line
    ])

    assert len(record_list) == 1
    assert record_list[0]["f_name"] == "FirstName"
    assert malformed_lines == []


def testBuildRecordListSkipsBlankLines(header_line, data_line):
    """Tests that blank lines are ignored."""

    record_list, malformed_lines = buildRecordList([
        header_line,
        data_line,
        "",
        "   "
    ])

    assert len(record_list) == 1
    assert malformed_lines == []


# Tests for matching duplicate customer records.

def testFindMatchingKeyMatchesEmail(valid_record):
    """Tests finding a duplicate by email address."""

    existing_records = {0: dict(valid_record)}
    candidate = dict(valid_record)
    candidate["primary_phone"] = "555-555-9999"

    assert findMatchingKey(candidate, existing_records) == 0


def testFindMatchingKeyMatchesPhone(valid_record):
    """Tests finding a duplicate by primary phone."""

    existing_records = {0: dict(valid_record)}
    candidate = dict(valid_record)
    candidate["email_address"] = "different@email.com"

    assert findMatchingKey(candidate, existing_records) == 0


def testMergeFillsBlankFields(valid_record):
    """Tests that a blank field is filled from the matching record"""

    first_record = dict(valid_record)
    first_record["secondary_phone"] = ""

    merged_record = mergeRecords(first_record, valid_record)

    assert merged_record["secondary_phone"] == "555-555-0101"


def testMergeKeepsLongerFirstName(valid_record):
    """Tests that the longer first name survives a merge"""

    short_name_record = dict(valid_record)
    short_name_record["f_name"] = "Dan"

    long_name_record = dict(valid_record)
    long_name_record["f_name"] = "Daniel"

    assert mergeRecords(short_name_record, long_name_record)["f_name"] == "Daniel"
    assert mergeRecords(long_name_record, short_name_record)["f_name"] == "Daniel"


# Tests for removing duplicate customer records.

def testRemoveDuplicatesMergesMatchingRecords(valid_record):
    """Tests that records sharing an identifier are merged."""

    first_record = dict(valid_record)

    second_record = dict(valid_record)
    second_record["email_address"] = "different@email.com"

    unique_records, merge_count = removeDuplicates([
        first_record,
        second_record
    ])

    assert len(unique_records) == 1
    assert merge_count == 1


def testRemoveDuplicatesKeepsDifferentPeople(valid_record):
    """Tests that records with different identifiers stay separate."""

    first_record = dict(valid_record)

    second_record = dict(valid_record)
    second_record["email_address"] = "other@email.com"
    second_record["primary_phone"] = "555-555-9999"

    unique_records, merge_count = removeDuplicates([
        first_record,
        second_record
    ])

    assert len(unique_records) == 2
    assert merge_count == 0


def testValidateRecordListSplitsRecords(valid_record):
    """Tests that records are separated into accepted and rejected lists"""

    bad_record = dict(valid_record)
    bad_record["state"] = "ZZ"
    bad_record["email_address"] = "other@email.com"

    accepted, rejected = validateRecordList([valid_record, bad_record])

    assert len(accepted) == 1
    assert len(rejected) == 1
    assert rejected[0][1] == ["state"]


def testReadDataFileHandlesMissingFile():
    """Tests that a file that does not exist returns no lines"""

    assert readDataFile("text_files/no_such_file.txt") == []


def testImportDataFileHandlesMissingFile():
    """Tests that an import of a missing file returns empty results"""

    accepted, rejected, counts = importDataFile("text_files/no_such_file.txt")

    assert accepted == []
    assert rejected == []
    assert counts == {}