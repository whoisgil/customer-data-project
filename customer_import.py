# menu driven application for importing and managing customer data
# importing needed libraries
from getpass import getpass
from pathlib import Path

from pymysql import MySQLError

from classes.db_connect import DB_Connect
from functions.import_functions import *
from functions.customer_functions import *
from functions.export_functions import writeExportFiles


show_debug_information = False

# Use absolute paths so exports work from any starting directory.

PROJECT_DIRECTORY = Path(__file__).resolve().parent
TEXT_FILE_DIRECTORY = PROJECT_DIRECTORY / "text_files"

PHONE_JSON_PATH = TEXT_FILE_DIRECTORY / "customer_phone.json"
LOCATION_CSV_PATH = TEXT_FILE_DIRECTORY / "customer_location.csv"


# connecting to the database

def createDatabaseConnection():
    """Prompts for credentials until a database connection succeeds."""

    # Retry the login so incorrect credentials do not end the program.
    while True:
        username = input("Database username: ").strip()
        password = getpass("Database password: ")

        database = DB_Connect(username, password, "python_projects")

        try:
            database.executeSelectQuery("SELECT 1")
            print("Database connection successful.")
            return database

        except MySQLError as error:
            error_code = error.args[0]

            if error_code in (1044, 1045):
                print("Login failed. Please check your username and password.")
            else:
                print("The database is unavailable. Please check that it is running.")


def showMenu():
    """Prints the main menu and returns the option the user chose"""

    print("")
    print("Customer Data Import Application")
    print("-----------------")
    print("1. Import a new data file")
    print("2. Show data currently in a database table")
    print("3. Add a record to the database tables")
    print("4. Edit a record")
    print("5. Delete a record")
    print("6. Quit the program")
    print("")

    return input("Please choose an option: ").strip()

def reportImportResults(passed_rejected, passed_counts):
    """Prints how many records were read, merged, accepted and rejected"""

    print("")
    print("Import Results")
    print("-----------------")
    print("Records read:     " + str(passed_counts["read"]))
    print("Records merged:   " + str(passed_counts["merged"]))
    print("Records accepted: " + str(passed_counts["accepted"]))
    print("Records rejected: " + str(passed_counts["rejected"]))

    if len(passed_rejected) > 0:
        print("")
        print("Rejected Records")
        print("-----------------")

        for current_record, failed_fields in passed_rejected:
            print(current_record["f_name"] + " " + current_record["l_name"] +
                  " failed on: " + ", ".join(failed_fields))

# Function for running the customer data import process.

def runImport(passed_db):
    """Imports a file, writes export files, and loads both database tables."""

    file_path = input(
        "Please enter the location of the data file: "
    ).strip()

    if not file_path:
        print("No file location was entered.")
        return

    accepted_records, rejected_records, import_counts = importDataFile(
        file_path
    )

    if not import_counts:
        return

    reportImportResults(
        rejected_records,
        import_counts
    )

    phone_written, location_written = writeExportFiles(
        accepted_records,
        PHONE_JSON_PATH,
        LOCATION_CSV_PATH
    )

    database_loaded = False

    # Load the database only after both required exports succeed.
    if phone_written and location_written:
        database_loaded = loadDatabaseTables(
            passed_db,
            accepted_records
        )
    else:
        print(
            "The database was not changed because "
            "an export file failed."
        )

    print()
    print("Phone JSON file written:   " + str(phone_written))
    print("Location CSV file written: " + str(location_written))
    print("Database tables loaded:    " + str(database_loaded))

def main():
    """Runs the menu until the user chooses to quit"""

    database = createDatabaseConnection()
    keep_running = True

    # Repeat the menu so only option 6 ends the program.
    while keep_running:

        chosen_option = showMenu()

        if chosen_option == "1":
            runImport(database)

        elif chosen_option == "2":
            chosen_table = chooseTable()
            if chosen_table:
                showTableRecords(database, chosen_table)

        elif chosen_option == "3":
            addCustomerRecord(database)

        elif chosen_option == "4":
            chosen_table = chooseTable()
            if chosen_table:
                editCustomerRecord(database, chosen_table)

        elif chosen_option == "5":
            chosen_table = chooseTable()
            if chosen_table:
               deleteCustomerRecord(database, chosen_table)

        elif chosen_option == "6":
            print("Goodbye.")
            keep_running = False

        else:
            print("That is not a valid option.")


if __name__ == "__main__":
    main()
    

