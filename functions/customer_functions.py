# Functions for clearing and loading customer records into the database
from functions.validation_functions import (
    validateName,
    validateCompany,
    validateAddress,
    validateCity,
    validateState,
    validateZip,
    validatePhone,
    validateEmail,
    validateFieldLength
)

show_debug_information = False


def clearDatabaseTables(passed_db):
    """Deletes every row from crm_data and Mailings."""

    passed_db.executeQuery("DELETE FROM Mailings")
    passed_db.executeQuery("DELETE FROM crm_data")


def loadDatabaseTables(passed_db, passed_records):
    """Clears both tables and loads the accepted records as one transaction."""

    crm_insert = (
        "INSERT INTO crm_data "
        "(f_name, l_name, address, city, state, zip, company, "
        "primary_phone, secondary_phone, email_address) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    mailings_insert = (
        "INSERT INTO Mailings (name, company, address) "
        "VALUES (%s, %s, %s)"
    )

    crm_param_list = []
    mailings_param_list = []

    # Convert blank optional values to SQL NULL.
    for current_record in passed_records:
        crm_param_list.append((
            current_record["f_name"],
            current_record["l_name"],
            current_record["address"],
            current_record["city"],
            current_record["state"],
            int(current_record["zip"]),
            current_record["company"] or None,
            current_record["primary_phone"],
            current_record["secondary_phone"] or None,
            current_record["email_address"] or None
        ))

        mailing_name = (
            current_record["f_name"] + " " + current_record["l_name"]
        )

        mailings_param_list.append((
            mailing_name,
            current_record["company"],
            current_record["address"]
        ))

    # Use one transaction so both database tables remain consistent.
    try:
        clearDatabaseTables(passed_db)

        passed_db.executeManyQuery(
            crm_insert,
            crm_param_list
        )

        passed_db.executeManyQuery(
            mailings_insert,
            mailings_param_list
        )

        passed_db.commit()
        return True

    except Exception as error:
        passed_db.rollback()

        if show_debug_information:
            print(error)
        else:
            print("The database tables could not be loaded.")

        return False


VALID_TABLES = ("crm_data", "Mailings")


def chooseTable():
    """Asks the user which database table to work with."""

    print()
    chosen_table = input(
        "Which table? (crm_data or Mailings): "
    ).strip()

    if chosen_table not in VALID_TABLES:
        print("That is not a valid table name.")
        return ""

    return chosen_table


def showTableRecords(passed_db, passed_table_name):
    """Displays every record in the chosen database table."""

    if passed_table_name not in VALID_TABLES:
        print("That is not a valid table name.")
        return

    try:
        # Table names cannot use placeholders, so only whitelisted names are allowed.
        table_rows = passed_db.executeSelectQuery(
            "SELECT * FROM " + passed_table_name
        )

    except Exception as error:
        if show_debug_information:
            print(error)
        else:
            print("The database table could not be read.")
        return

    if not table_rows:
        print("That table has no records.")
        return

    print()

    for current_row in table_rows:
        print(current_row)


# Functions for adding a new customer record.

def promptValidField(
    passed_prompt,
    passed_validator,
    passed_max_length=50,
    passed_allow_blank=False
):
    """Prompts until a field passes validation."""

    while True:
        entered_value = input(passed_prompt).strip()

        if passed_allow_blank and not entered_value:
            return entered_value

        if not validateFieldLength(entered_value, passed_max_length):
            print(
                "That value is too long (limit is "
                + str(passed_max_length)
                + " characters)."
            )
            continue

        if not passed_validator(entered_value):
            print("That value is not valid, please try again.")
            continue

        return entered_value


def promptForRecord():
    """Prompts for all customer fields."""

    while True:
      f_name = promptValidField(
          "First name: ",
          validateName
      )

      l_name = promptValidField(
          "Last name: ",
          validateName
      )

      mailing_name = f_name + " " + l_name

      if validateFieldLength(mailing_name, 50):
          break

      print(
          "The combined first and last name must be "
          "50 characters or fewer."
      )

    company = promptValidField(
        "Company (optional): ",
        validateCompany,
        passed_allow_blank=True
    )

    address = promptValidField("Address: ", validateAddress)
    city = promptValidField("City: ", validateCity)

    while True:
        state = input(
            "State (two-letter abbreviation): "
        ).strip().upper()

        if validateState(state):
            break

        print("That is not a valid state abbreviation.")

    zip_code = promptValidField(
        "ZIP code: ",
        validateZip
    )

    primary_phone = promptValidField(
        "Primary phone: ",
        validatePhone
    )

    secondary_phone = promptValidField(
        "Secondary phone (optional): ",
        validatePhone,
        passed_allow_blank=True
    )

    email_address = promptValidField(
        "Email address (optional): ",
        validateEmail,
        passed_allow_blank=True
    )

    return {
        "f_name": f_name,
        "l_name": l_name,
        "company": company,
        "address": address,
        "city": city,
        "state": state,
        "zip": zip_code,
        "primary_phone": primary_phone,
        "secondary_phone": secondary_phone,
        "email_address": email_address
    }

# One transaction ensures the customer is added to both tables or neither table.
def insertRecordBothTables(passed_db, passed_record):
    """Inserts one customer into both tables as one transaction."""

    crm_insert = (
        "INSERT INTO crm_data "
        "(f_name, l_name, address, city, state, zip, company, "
        "primary_phone, secondary_phone, email_address) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    )

    crm_params = (
        passed_record["f_name"],
        passed_record["l_name"],
        passed_record["address"],
        passed_record["city"],
        passed_record["state"],
        int(passed_record["zip"]),
        passed_record["company"] or None,
        passed_record["primary_phone"],
        passed_record["secondary_phone"] or None,
        passed_record["email_address"] or None
    )

    mailing_name = (
        passed_record["f_name"]
        + " "
        + passed_record["l_name"]
    )

    mailings_insert = (
        "INSERT INTO Mailings "
        "(name, company, address) "
        "VALUES (%s, %s, %s)"
    )

    mailings_params = (
        mailing_name,
        passed_record["company"],
        passed_record["address"]
    )

    try:
        passed_db.executeQuery(
            crm_insert,
            crm_params
        )

        passed_db.executeQuery(
            mailings_insert,
            mailings_params
        )

        passed_db.commit()
        return True

    except Exception as error:
        passed_db.rollback()

        if show_debug_information:
            print(error)
        else:
            print("The record could not be saved to the database.")

        return False


def addCustomerRecord(passed_db):
    """Runs the add-customer workflow."""

    new_record = promptForRecord()

    if insertRecordBothTables(passed_db, new_record):
        print("The record was added to both tables.")


PRIMARY_KEY_COLUMNS = {
    "crm_data": "crm_id",
    "Mailings": "mail_id"
}

EDITABLE_COLUMNS = {
    "crm_data": [
        "f_name", "l_name", "company", "address", "city",
        "state", "zip", "primary_phone", "secondary_phone",
        "email_address"
    ],
    "Mailings": ["name", "company", "address"]
}

OPTIONAL_FIELDS = {"company", "secondary_phone", "email_address"}

FIELD_VALIDATORS = {
    "f_name": validateName,
    "l_name": validateName,
    "name": validateName,
    "company": validateCompany,
    "address": validateAddress,
    "city": validateCity,
    "zip": validateZip,
    "primary_phone": validatePhone,
    "secondary_phone": validatePhone,
    "email_address": validateEmail
}


def fetchRecordById(passed_db, passed_table, passed_record_id):
    """Returns the record with the given ID from the chosen table, or None"""

    primary_key = PRIMARY_KEY_COLUMNS[passed_table]

    try:
        matching_rows = passed_db.executeSelectQuery(
            "SELECT * FROM " + passed_table + " WHERE " + primary_key + " = %s",
            (passed_record_id,)
        )

    except Exception as error:
        if show_debug_information:
            print(error)
        else:
            print("The record could not be read.")
        return None

    if not matching_rows:
        return None

    return matching_rows[0]


def promptRecordId(passed_table):
    """Prompts for the primary key value of the record to edit or delete"""

    primary_key = PRIMARY_KEY_COLUMNS[passed_table]
    entered_value = input(
        "Enter the " + primary_key + " of the record: "
    ).strip()

    if not entered_value.isdigit():
        print("That is not a valid ID.")
        return None

    return int(entered_value)


def promptFieldName(passed_table):
    """Asks which field to edit and returns the matching column name"""

    editable_columns = EDITABLE_COLUMNS[passed_table]

    print()
    print("Which field would you like to edit?")

    for current_index, current_column in enumerate(editable_columns, start=1):
        print(str(current_index) + ". " + current_column)

    chosen_index = input("Please choose a field: ").strip()

    if not chosen_index.isdigit():
        print("That is not a valid choice.")
        return ""

    chosen_index = int(chosen_index)

    if chosen_index < 1 or chosen_index > len(editable_columns):
        print("That is not a valid choice.")
        return ""

    return editable_columns[chosen_index - 1]


def promptFieldValue(passed_field_name):
    """Prompts for a new value for the chosen field, validating it appropriately"""

    if passed_field_name == "state":
        while True:
            new_value = input(
                "New state (two-letter abbreviation): "
            ).strip().upper()

            if validateState(new_value):
                return new_value

            print("That is not a valid state abbreviation.")

    validator = FIELD_VALIDATORS[passed_field_name]
    allow_blank = passed_field_name in OPTIONAL_FIELDS
    max_length = 5 if passed_field_name == "zip" else 50

    return promptValidField(
        "New " + passed_field_name + ": ",
        validator,
        passed_max_length=max_length,
        passed_allow_blank=allow_blank
    )

def updateRecordField(passed_db, passed_table, passed_record_id, passed_field_name, passed_new_value):
    """Updates one field on one record and reports whether it succeeded"""

    if passed_field_name not in EDITABLE_COLUMNS.get(passed_table, []):
        print("That field cannot be edited.")
        return False

    primary_key = PRIMARY_KEY_COLUMNS[passed_table]
    stored_value = int(passed_new_value) if passed_field_name == "zip" else (passed_new_value or None)

    # Only approved table and column names reach SQL; the new value stays parameterized.
    update_query = (
        "UPDATE " + passed_table
        + " SET " + passed_field_name + " = %s"
        + " WHERE " + primary_key + " = %s"
    )

    try:
        passed_db.executeQuery(update_query, (stored_value, passed_record_id))
        passed_db.commit()
        return True

    except Exception as error:
        passed_db.rollback()

        if show_debug_information:
            print(error)
        else:
            print("The record could not be updated.")

        return False


def editCustomerRecord(passed_db, passed_table):
    """Runs the edit-record workflow for the chosen table"""

    showTableRecords(passed_db, passed_table)

    record_id = promptRecordId(passed_table)
    if record_id is None:
        return

    record = fetchRecordById(passed_db, passed_table, record_id)
    if not record:
        print("No record was found with that ID.")
        return

    field_name = promptFieldName(passed_table)
    if not field_name:
        return

    new_value = promptFieldValue(field_name)

    if updateRecordField(passed_db, passed_table, record_id, field_name, new_value):
        print("The record was updated.")


def deleteRecordById(passed_db, passed_table, passed_record_id):
    """Deletes one record by ID and reports whether it succeeded"""

    primary_key = PRIMARY_KEY_COLUMNS[passed_table]

    # Parameterize user values to prevent SQL injection.
    delete_query = "DELETE FROM " + passed_table + " WHERE " + primary_key + " = %s"

    try:
        passed_db.executeQuery(delete_query, (passed_record_id,))
        passed_db.commit()
        return True

    except Exception as error:
        passed_db.rollback()

        if show_debug_information:
            print(error)
        else:
            print("The record could not be deleted.")

        return False


def deleteCustomerRecord(passed_db, passed_table):
    """Runs the delete-record workflow for the chosen table"""

    showTableRecords(passed_db, passed_table)

    record_id = promptRecordId(passed_table)
    if record_id is None:
        return

    record = fetchRecordById(passed_db, passed_table, record_id)
    if not record:
        print("No record was found with that ID.")
        return

    print()
    print(record)

    # Require confirmation because deleting a record cannot be undone.
    confirmation = input("Type yes to delete this record: ").strip().lower()

    if confirmation != "yes":
        print("The record was not deleted.")
        return

    if deleteRecordById(passed_db, passed_table, record_id):
        print("The record was deleted.")

   