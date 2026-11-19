# pytest test cases for the customer database functions

# importing needed libraries
from unittest.mock import Mock, patch

import pytest

from functions.customer_functions import *


@pytest.fixture
def valid_record():
    """Builds a valid customer record used by the tests"""

    return {
        "f_name": "FirstName",
        "l_name": "LastName",
        "company": "Company",
        "address": "123 Address St",
        "city": "City",
        "state": "PA",
        "zip": "15601",
        "primary_phone": "555-555-0100",
        "secondary_phone": "555-555-0101",
        "email_address": "test@email.com"
    }


# Tests for clearing, loading, and showing database records.

def testClearDatabaseTables():
    """Tests that both tables are cleared in the required order"""

    database = Mock()
    clearDatabaseTables(database)

    assert database.executeQuery.call_count == 2

    first_query = database.executeQuery.call_args_list[0].args[0]
    second_query = database.executeQuery.call_args_list[1].args[0]

    assert first_query == "DELETE FROM Mailings"
    assert second_query == "DELETE FROM crm_data"


def testLoadDatabaseTables(valid_record):
    """Tests that records are loaded into both tables and committed"""

    database = Mock()

    assert loadDatabaseTables(database, [valid_record])
    assert database.executeManyQuery.call_count == 2

    crm_params = database.executeManyQuery.call_args_list[0].args[1][0]
    mailing_params = database.executeManyQuery.call_args_list[1].args[1][0]

    assert crm_params[5] == 15601

    assert mailing_params == (
        "FirstName LastName",
        "Company",
        "123 Address St"
    )

    database.commit.assert_called_once_with()
    database.rollback.assert_not_called()


def testLoadDatabaseTablesRollsBackOnFailure(valid_record):
    """Tests that a failed table load rolls back the transaction"""

    database = Mock()
    database.executeManyQuery.side_effect = RuntimeError("database error")

    assert not loadDatabaseTables(database, [valid_record])

    database.rollback.assert_called_once_with()
    database.commit.assert_not_called()


def testShowTableRecords(capsys):
    """Tests that each database row is printed individually"""

    database = Mock()
    table_rows = [
        {"crm_id": 1, "f_name": "FirstName"},
        {"crm_id": 2, "f_name": "Second"}
    ]

    database.executeSelectQuery.return_value = table_rows

    showTableRecords(database, "crm_data")
    printed_output = capsys.readouterr().out

    database.executeSelectQuery.assert_called_once_with(
        "SELECT * FROM crm_data"
    )

    assert str(table_rows[0]) in printed_output
    assert str(table_rows[1]) in printed_output


# Tests for adding customer records.

def testInsertRecordBothTables(valid_record):
    """Tests that one customer is inserted into both tables"""

    database = Mock()

    assert insertRecordBothTables(database, valid_record)
    assert database.executeQuery.call_count == 2

    crm_query = database.executeQuery.call_args_list[0].args[0]
    mailing_query = database.executeQuery.call_args_list[1].args[0]
    crm_params = database.executeQuery.call_args_list[0].args[1]
    mailing_params = database.executeQuery.call_args_list[1].args[1]

    assert "INSERT INTO crm_data" in crm_query
    assert "INSERT INTO Mailings" in mailing_query
    assert crm_params[5] == 15601

    assert mailing_params == (
        "FirstName LastName",
        "Company",
        "123 Address St"
    )

    database.commit.assert_called_once_with()
    database.rollback.assert_not_called()


def testInsertRecordBothTablesRollsBackOnFailure(valid_record):
    """Tests that a failed insert rolls back both table changes"""

    database = Mock()
    database.executeQuery.side_effect = RuntimeError("database error")

    assert not insertRecordBothTables(database, valid_record)

    database.rollback.assert_called_once_with()
    database.commit.assert_not_called()


# Tests for editing customer records.

def testUpdateRecordField():
    """Tests that one selected field is updated and committed"""

    database = Mock()

    assert updateRecordField(database, "crm_data", 7, "zip", "15601")

    expected_query = "UPDATE crm_data SET zip = %s WHERE crm_id = %s"

    database.executeQuery.assert_called_once_with(
        expected_query, (15601, 7)
    )

    database.commit.assert_called_once_with()
    database.rollback.assert_not_called()


def testUpdateRecordFieldRollsBackOnFailure():
    """Tests that a failed update rolls back the transaction"""

    database = Mock()
    database.executeQuery.side_effect = RuntimeError("database error")

    assert not updateRecordField(
        database, "crm_data", 7, "city", "New City"
    )

    database.rollback.assert_called_once_with()
    database.commit.assert_not_called()


def testEditCustomerRecord():
    """Tests the complete edit-record workflow"""

    database = Mock()
    selected_record = {"crm_id": 7, "f_name": "FirstName"}

    with (
        patch("functions.customer_functions.showTableRecords"),
        patch(
            "functions.customer_functions.promptRecordId",
            return_value=7
        ),
        patch(
            "functions.customer_functions.fetchRecordById",
            return_value=selected_record
        ),
        patch(
            "functions.customer_functions.promptFieldName",
            return_value="city"
        ),
        patch(
            "functions.customer_functions.promptFieldValue",
            return_value="New City"
        ),
        patch(
            "functions.customer_functions.updateRecordField",
            return_value=True
        ) as mock_update
    ):
        editCustomerRecord(database, "crm_data")

    mock_update.assert_called_once_with(
        database, "crm_data", 7, "city", "New City"
    )


# Tests for deleting customer records.

def testDeleteRecordById():
    """Tests that one selected record is deleted and committed"""

    database = Mock()

    assert deleteRecordById(database, "Mailings", 4)

    expected_query = "DELETE FROM Mailings WHERE mail_id = %s"

    database.executeQuery.assert_called_once_with(expected_query, (4,))
    database.commit.assert_called_once_with()
    database.rollback.assert_not_called()


def testDeleteRecordByIdRollsBackOnFailure():
    """Tests that a failed deletion rolls back the transaction"""

    database = Mock()
    database.executeQuery.side_effect = RuntimeError("database error")

    assert not deleteRecordById(database, "crm_data", 7)

    database.rollback.assert_called_once_with()
    database.commit.assert_not_called()


def testDeleteCustomerRecordRequiresConfirmation():
    """Tests that deletion requires confirmation from the user"""

    database = Mock()
    selected_record = {"crm_id": 7, "f_name": "FirstName"}

    with (
        patch("functions.customer_functions.showTableRecords"),
        patch(
            "functions.customer_functions.promptRecordId",
            return_value=7
        ),
        patch(
            "functions.customer_functions.fetchRecordById",
            return_value=selected_record
        ),
        patch(
            "functions.customer_functions.deleteRecordById",
            return_value=True
        ) as mock_delete
    ):
        with patch("builtins.input", return_value="no"):
            deleteCustomerRecord(database, "crm_data")
            mock_delete.assert_not_called()

        with patch("builtins.input", return_value="yes"):
            deleteCustomerRecord(database, "crm_data")

    mock_delete.assert_called_once_with(database, "crm_data", 7)