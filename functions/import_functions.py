# functions for importing and cleaning the customer data file

# importing needed libraries
from pathlib import Path
from functions.validation_functions import *

show_debug_information = False


def readDataFile(passed_file_path):
    """Reads the data file and returns its lines, or an empty list if it cannot be read"""

    source_file = Path(passed_file_path)

    try:
        file_contents = source_file.read_text(encoding="utf-8")
        return file_contents.splitlines()

    except FileNotFoundError:
        if show_debug_information:
            print("-----------------")
            print("DEBUG INFORMATION")
            print("-----------------")
            print("The file was not found at " + str(source_file))
        else:
            print("That file could not be found.")
        return []

    except PermissionError:
        if show_debug_information:
            print("-----------------")
            print("DEBUG INFORMATION")
            print("-----------------")
            print("Permission was denied reading " + str(source_file))
        else:
            print("That file could not be opened.")
        return []

    except UnicodeDecodeError:
        if show_debug_information:
            print("-----------------")
            print("DEBUG INFORMATION")
            print("-----------------")
            print("The file is not readable as text")
        else:
            print("That file is not a readable text file.")
        return []


def parseLine(passed_line):
    """Splits one line of the data file into a customer record, or returns an empty dictionary"""

    # Split here because the source system uses two backslashes between fields.
    raw_fields = passed_line.split("\\\\")

    if len(raw_fields) < 11:
        return {}

    cleaned_fields = []

    for current_field in raw_fields:
        current_field = current_field.strip()
        current_field = current_field.removeprefix("##")
        current_field = current_field.removesuffix("##")
        cleaned_fields.append(current_field.strip())

    customer_record = {"f_name": cleaned_fields[0],
                       "l_name": cleaned_fields[1],
                       "company": cleaned_fields[2],
                       "address": cleaned_fields[3],
                       "city": cleaned_fields[4],
                       "county": cleaned_fields[5],
                       "state": cleaned_fields[6],
                       "zip": cleaned_fields[7],
                       "primary_phone": cleaned_fields[8],
                       "secondary_phone": cleaned_fields[9],
                       "email_address": cleaned_fields[10]}

    return customer_record


def cleanRecord(passed_record):
    """Repairs the values in a record where the correction has one clear answer"""

    cleaned_record = {}

    for current_field in passed_record:
        cleaned_record[current_field] = passed_record[current_field].strip()

    cleaned_record["state"] = cleaned_record["state"].upper()
    cleaned_record["email_address"] = cleaned_record["email_address"].lower()

    return cleaned_record


# Functions for building and cleaning the imported record list.

def buildRecordList(passed_lines):
    """Builds cleaned customer records and tracks malformed lines"""

    customer_records = []
    malformed_lines = []

    # Skip the first line because it contains headings instead of customer data.
    for current_line in passed_lines[1:]:

        if not current_line.strip():
            continue

        parsed_record = parseLine(current_line)

        if not parsed_record:
            malformed_lines.append(current_line)
            continue

        customer_records.append(cleanRecord(parsed_record))

    return customer_records, malformed_lines


# Functions for finding and merging duplicate customer records.

def findMatchingKey(passed_record, passed_unique_records):
    """Returns the key of a record matching by email or phone."""

    email = passed_record["email_address"]
    phone = passed_record["primary_phone"]

    # Use email or phone because duplicate customer names may be shortened.

    for current_key, current_record in passed_unique_records.items():

        if email and current_record["email_address"] == email:
            return current_key

        if phone and current_record["primary_phone"] == phone:
            return current_key

    return None


def mergeRecords(passed_existing, passed_duplicate):
    """Combines two records for the same person into one"""

    merged_record = {}

    for current_field in passed_existing:

        existing_value = passed_existing[current_field]
        duplicate_value = passed_duplicate[current_field]

        # Fill blank fields from duplicates so no information is lost.
        if len(existing_value) == 0:
            merged_record[current_field] = duplicate_value
        else:
            merged_record[current_field] = existing_value

    # Keep the longer name because it contains more information.
    if len(passed_duplicate["f_name"]) > len(passed_existing["f_name"]):
        merged_record["f_name"] = passed_duplicate["f_name"]

    return merged_record


def removeDuplicates(passed_records):
    """Merges records that describe the same customer."""

    unique_records = {}
    record_order = []
    next_key = 0
    merge_count = 0

    for current_record in passed_records:
        matching_key = findMatchingKey(
            current_record,
            unique_records
        )

        if matching_key is not None:
            unique_records[matching_key] = mergeRecords(
                unique_records[matching_key],
                current_record
            )
            merge_count += 1

        else:
            unique_records[next_key] = current_record
            record_order.append(next_key)
            next_key += 1

    merged_list = []

    for current_key in record_order:
        merged_list.append(unique_records[current_key])

    return merged_list, merge_count


def validateRecordList(passed_records):
    """Splits a list of records into the ones that passed validation and the ones that failed"""

    accepted_records = []
    rejected_records = []

    for current_record in passed_records:

        failed_fields = validateRecord(current_record)

        if len(failed_fields) == 0:
            accepted_records.append(current_record)
        else:
            rejected_records.append((current_record, failed_fields))

    return accepted_records, rejected_records


def importDataFile(passed_file_path):
    """Imports customer data and returns records and import counts."""

    file_lines = readDataFile(passed_file_path)

    if not file_lines:
        return [], [], {}

    all_records, malformed_lines = buildRecordList(file_lines)

    # Merge before validation so duplicates can fill missing fields.
    unique_records, merge_count = removeDuplicates(
        all_records
    )

    accepted_records, rejected_records = validateRecordList(
        unique_records
    )

    for current_line in malformed_lines:
        rejected_records.append((
            {
                "f_name": "(unreadable)",
                "l_name": "row"
            },
            ["malformed row"]
        ))

    import_counts = {
        "read": len(all_records) + len(malformed_lines),
        "merged": merge_count,
        "accepted": len(accepted_records),
        "rejected": len(rejected_records)
        }

    return accepted_records, rejected_records, import_counts