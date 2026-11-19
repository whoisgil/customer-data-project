# functions for exporting customer records to JSON and CSV output files

#importing needed libraries
import csv
import json
import shutil
from pathlib import Path

show_debug_information = False

# Back up existing exports so the previous files can be recovered.
def backupExistingFile(passed_file_path):
    """Copies an existing output file to a .copy file before it gets overwritten"""

    target_file = Path(passed_file_path)

    if not target_file.exists():
        return True

    backup_path = target_file.with_suffix(target_file.suffix + ".copy")

    try:
        shutil.copy2(target_file, backup_path)
        return True

    except OSError as error:
        if show_debug_information:
            print(error)
        else:
            print("The existing output file could not be backed up.")
        return False



def writePhoneJson(passed_records, passed_file_path):
    """Writes first name and phone numbers for every accepted record to a JSON file."""

    phone_records = []

    # Include only the fields permitted in the JSON output.
    for current_record in passed_records:
        phone_numbers = []

        if current_record["primary_phone"]:
            phone_numbers.append(current_record["primary_phone"])

        if current_record["secondary_phone"]:
            phone_numbers.append(current_record["secondary_phone"])

        phone_records.append({
            "first_name": current_record["f_name"],
            "phone_numbers": phone_numbers
        })


    if not backupExistingFile(passed_file_path):
        return False

    try:
        with open(passed_file_path, "w", encoding="utf-8") as output_file:
            json.dump(phone_records, output_file, indent=2)

        return True

    except (OSError, TypeError) as error:
        if show_debug_information:
            print(error)
        else:
            print("The phone JSON file could not be written.")

        return False 



def writeLocationCsv(passed_records, passed_file_path):
    """Writes first name, last name, county and state to a CSV file."""

    if not backupExistingFile(passed_file_path):
        return False
    
    try:
        with open(passed_file_path, "w", encoding="utf-8", newline="") as output_file:
            csv_writer = csv.writer(output_file)

            csv_writer.writerow([
                "first_name", "last_name", "county", "state"
            ])

            # Include only the fields permitted in the CSV output.
            for current_record in passed_records:
                csv_writer.writerow([
                    current_record["f_name"],
                    current_record["l_name"],
                    current_record["county"],
                    current_record["state"]
                ])

        return True

    except (OSError, csv.Error) as error:
        if show_debug_information:
            print(error)
        else:
            print("The location CSV file could not be written.")
        return False

def writeExportFiles(passed_records, passed_phone_path, passed_location_path):
    """Writes both output files for the accepted records and reports whether each succeeded"""

    phone_written = writePhoneJson(passed_records, passed_phone_path)
    location_written = writeLocationCsv(passed_records, passed_location_path)

    return phone_written, location_written