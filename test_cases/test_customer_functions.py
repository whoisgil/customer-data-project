# unittest test cases for the customer database functions

# importing needed libraries
import unittest
from unittest.mock import Mock, patch

from functions.customer_functions import *


class TestCustomerFunctions(unittest.TestCase):
    """Test cases covering the customer database functions"""

    def setUp(self):
        """Builds a valid customer record used by the tests"""

        self.valid_record = {
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

    def testClearDatabaseTables(self):
        """Tests that both tables are cleared in the required order"""

        database = Mock()
        clearDatabaseTables(database)

        self.assertEqual(database.executeQuery.call_count, 2)

        first_query = database.executeQuery.call_args_list[0].args[0]
        second_query = database.executeQuery.call_args_list[1].args[0]

        self.assertEqual(first_query, "DELETE FROM Mailings")
        self.assertEqual(second_query, "DELETE FROM crm_data")

    def testLoadDatabaseTables(self):
        """Tests that records are loaded into both tables and committed"""

        database = Mock()

        self.assertTrue(loadDatabaseTables(database, [self.valid_record]))
        self.assertEqual(database.executeManyQuery.call_count, 2)

        crm_params = database.executeManyQuery.call_args_list[0].args[1][0]
        mailing_params = database.executeManyQuery.call_args_list[1].args[1][0]

        self.assertEqual(crm_params[5], 15601)

        self.assertEqual(
            mailing_params,
            ("FirstName LastName", "Company", "123 Address St")
        )

        database.commit.assert_called_once_with()
        database.rollback.assert_not_called()

    def testLoadDatabaseTablesRollsBackOnFailure(self):
        """Tests that a failed table load rolls back the transaction"""

        database = Mock()
        database.executeManyQuery.side_effect = RuntimeError("database error")

        self.assertFalse(loadDatabaseTables(database, [self.valid_record]))

        database.rollback.assert_called_once_with()
        database.commit.assert_not_called()

    def testShowTableRecords(self):
        """Tests that each database row is printed individually"""

        database = Mock()
        table_rows = [
            {"crm_id": 1, "f_name": "FirstName"},
            {"crm_id": 2, "f_name": "Second"}
        ]

        database.executeSelectQuery.return_value = table_rows

        with patch("builtins.print") as mock_print:
            showTableRecords(database, "crm_data")

        database.executeSelectQuery.assert_called_once_with(
            "SELECT * FROM crm_data"
        )

        mock_print.assert_any_call(table_rows[0])
        mock_print.assert_any_call(table_rows[1])

    # Tests for adding customer records.

    def testInsertRecordBothTables(self):
        """Tests that one customer is inserted into both tables"""

        database = Mock()

        self.assertTrue(insertRecordBothTables(database, self.valid_record))
        self.assertEqual(database.executeQuery.call_count, 2)

        crm_query = database.executeQuery.call_args_list[0].args[0]
        mailing_query = database.executeQuery.call_args_list[1].args[0]
        crm_params = database.executeQuery.call_args_list[0].args[1]
        mailing_params = database.executeQuery.call_args_list[1].args[1]

        self.assertIn("INSERT INTO crm_data", crm_query)
        self.assertIn("INSERT INTO Mailings", mailing_query)
        self.assertEqual(crm_params[5], 15601)

        self.assertEqual(
            mailing_params,
            ("FirstName LastName", "Company", "123 Address St")
        )

        database.commit.assert_called_once_with()
        database.rollback.assert_not_called()

    def testInsertRecordBothTablesRollsBackOnFailure(self):
        """Tests that a failed insert rolls back both table changes"""

        database = Mock()
        database.executeQuery.side_effect = RuntimeError("database error")

        self.assertFalse(insertRecordBothTables(database, self.valid_record))

        database.rollback.assert_called_once_with()
        database.commit.assert_not_called()

    # Tests for editing customer records.

    def testUpdateRecordField(self):
        """Tests that one selected field is updated and committed"""

        database = Mock()

        self.assertTrue(
            updateRecordField(database, "crm_data", 7, "zip", "15601")
        )

        expected_query = "UPDATE crm_data SET zip = %s WHERE crm_id = %s"

        database.executeQuery.assert_called_once_with(
            expected_query, (15601, 7)
        )

        database.commit.assert_called_once_with()
        database.rollback.assert_not_called()

    def testUpdateRecordFieldRollsBackOnFailure(self):
        """Tests that a failed update rolls back the transaction"""

        database = Mock()
        database.executeQuery.side_effect = RuntimeError("database error")

        self.assertFalse(
            updateRecordField(database, "crm_data", 7, "city", "New City")
        )

        database.rollback.assert_called_once_with()
        database.commit.assert_not_called()

    def testEditCustomerRecord(self):
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

    def testDeleteRecordById(self):
        """Tests that one selected record is deleted and committed"""

        database = Mock()

        self.assertTrue(deleteRecordById(database, "Mailings", 4))

        expected_query = "DELETE FROM Mailings WHERE mail_id = %s"

        database.executeQuery.assert_called_once_with(expected_query, (4,))
        database.commit.assert_called_once_with()
        database.rollback.assert_not_called()

    def testDeleteRecordByIdRollsBackOnFailure(self):
        """Tests that a failed deletion rolls back the transaction"""

        database = Mock()
        database.executeQuery.side_effect = RuntimeError("database error")

        self.assertFalse(deleteRecordById(database, "crm_data", 7))

        database.rollback.assert_called_once_with()
        database.commit.assert_not_called()

    def testDeleteCustomerRecordRequiresConfirmation(self):
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


if __name__ == "__main__":
    unittest.main()