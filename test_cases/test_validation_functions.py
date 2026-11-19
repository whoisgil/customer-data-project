# unittest test cases for the validation functions

# importing needed libraries
import unittest
from functions.validation_functions import *


class TestValidationFunctions(unittest.TestCase):

    def setUp(self):
        """Builds a valid record used by the record level tests"""

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

    def testValidNames(self):
        """Tests names that should pass validation"""

        self.assertTrue(validateName("FirstName"))
        self.assertTrue(validateName("Mary Anne"))
        self.assertTrue(validateName("O'Brien"))
        self.assertTrue(validateName("Smith-Jones"))

    def testInvalidNames(self):
        """Tests names that should fail validation"""

        self.assertFalse(validateName("Name3"))
        self.assertFalse(validateName("Name@Name"))
        self.assertFalse(validateName(""))

    def testValidCompanies(self):
        """Tests company names that should pass validation"""

        self.assertTrue(validateCompany("Company"))
        self.assertTrue(validateCompany("Smith & Sons, Inc."))
        self.assertTrue(validateCompany("Company #1 (Eastern)"))
        self.assertTrue(validateCompany(""))

    def testInvalidCompanies(self):
        """Tests company names that should fail validation"""

        self.assertFalse(validateCompany("Company~Name"))
        self.assertFalse(validateCompany("Company{Name}"))
        self.assertFalse(validateCompany("Company|Name"))

    def testValidAddresses(self):
        """Tests addresses that should pass validation"""

        self.assertTrue(validateAddress("123 Address St"))
        self.assertTrue(validateAddress("8 W Cerritos Ave #54"))
        self.assertTrue(validateAddress("9 Elm St, Apt (B)"))

    def testInvalidAddresses(self):
        """Tests addresses that should fail validation"""

        self.assertFalse(validateAddress("123 Address St!"))
        self.assertFalse(validateAddress("123 Address St*"))
        self.assertFalse(validateAddress(""))

    def testValidCities(self):
        """Tests city names that should pass validation"""

        self.assertTrue(validateCity("City"))
        self.assertTrue(validateCity("St. Louis"))
        self.assertTrue(validateCity("Coeur d'Alene"))
        self.assertTrue(validateCity("Winston-Salem"))

    def testInvalidCities(self):
        """Tests city names that should fail validation"""

        self.assertFalse(validateCity("City@Name"))
        self.assertFalse(validateCity("City Name!"))
        self.assertFalse(validateCity(""))

    def testValidStates(self):
        """Tests state abbreviations that should pass validation"""

        self.assertTrue(validateState("PA"))
        self.assertTrue(validateState("AL"))
        self.assertTrue(validateState("WY"))

    def testInvalidStates(self):
        """Tests state values that should fail validation"""

        self.assertFalse(validateState("pa"))
        self.assertFalse(validateState("Pennsylvania"))
        self.assertFalse(validateState(""))

    def testStatesNotAllowedAreRejected(self):
        """Tests that abbreviations outside the fifty accepted values are rejected"""

        self.assertFalse(validateState("PR"))
        self.assertFalse(validateState("GU"))
        self.assertFalse(validateState("ZZ"))

    def testValidZipFormat(self):
        """Tests ZIP codes that should pass validation"""

        self.assertTrue(validateZip("8014"))
        self.assertTrue(validateZip("15601"))

    def testInvalidZipFormat(self):
        """Tests ZIP codes that should fail validation"""

        self.assertFalse(validateZip("123"))
        self.assertFalse(validateZip("156011"))
        self.assertFalse(validateZip("1560A"))
        self.assertFalse(validateZip("15601-2201"))
        self.assertFalse(validateZip(""))

    def testValidPhoneFormat(self):
        """Tests phone numbers that should pass validation"""

        self.assertTrue(validatePhone("5555550100"))
        self.assertTrue(validatePhone("555-555-0100"))
        self.assertTrue(validatePhone("555.555.0100"))

    def testInvalidPhoneFormat(self):
        """Tests phone numbers that should fail validation"""

        self.assertFalse(validatePhone("555555010"))
        self.assertFalse(validatePhone("55555501000"))
        self.assertFalse(validatePhone("(555) 555-0100"))
        self.assertFalse(validatePhone("555-555-010x"))
        self.assertFalse(validatePhone(""))

    def testValidEmails(self):
        """Tests email addresses that should pass validation"""

        self.assertTrue(validateEmail("test@email.com"))
        self.assertTrue(validateEmail("first_last@email.org"))
        self.assertTrue(validateEmail("first.last-name+tag@email.net"))

    def testInvalidEmails(self):
        """Tests email addresses that should fail validation"""

        self.assertFalse(validateEmail("test address@email.com"))
        self.assertFalse(validateEmail("test@email!com"))
        self.assertFalse(validateEmail(""))

    def testFieldLength(self):
        """Tests the database column length guard"""

        self.assertTrue(validateFieldLength("FirstName LastName", 50))
        self.assertTrue(validateFieldLength("A" * 50, 50))
        self.assertFalse(validateFieldLength("A" * 51, 50))

    def testValidRecordPasses(self):
        """Tests that a clean record reports no failed fields"""

        self.assertEqual(validateRecord(self.valid_record), [])

    def testRecordReportsBadState(self):
        """Tests that a record with a bad state reports only that field"""

        self.valid_record["state"] = "ZZ"
        self.assertEqual(validateRecord(self.valid_record), ["state"])

    def testRecordAllowsEmptyOptionalFields(self):
        """Tests that blank optional fields do not fail the record"""

        self.valid_record["secondary_phone"] = ""
        self.valid_record["email_address"] = ""
        self.assertEqual(validateRecord(self.valid_record), [])

    def testRecordReportsMultipleFailures(self):
        """Tests that every failing field is reported"""

        self.valid_record["state"] = "ZZ"
        self.valid_record["zip"] = "ABC"
        self.assertEqual(validateRecord(self.valid_record), ["state", "zip"])


if __name__ == "__main__":
    unittest.main()