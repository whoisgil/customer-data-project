# pytest test cases for the validation functions

# importing needed libraries
import pytest
from functions.validation_functions import *


@pytest.fixture
def valid_record():
    """Builds a valid record used by the record level tests"""

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


def testValidNames():
    """Tests names that should pass validation"""

    assert validateName("FirstName") == True
    assert validateName("Mary Anne") == True
    assert validateName("O'Brien") == True
    assert validateName("Smith-Jones") == True


def testInvalidNames():
    """Tests names that should fail validation"""

    assert validateName("Name3") == False
    assert validateName("Name@Name") == False
    assert validateName("") == False


def testValidCompanies():
    """Tests company names that should pass validation"""

    assert validateCompany("Company") == True
    assert validateCompany("Smith & Sons, Inc.") == True
    assert validateCompany("Company #1 (Eastern)") == True
    assert validateCompany("") == True


def testInvalidCompanies():
    """Tests company names that should fail validation"""

    assert validateCompany("Company~Name") == False
    assert validateCompany("Company{Name}") == False
    assert validateCompany("Company|Name") == False


def testValidAddresses():
    """Tests addresses that should pass validation"""

    assert validateAddress("123 Address St") == True
    assert validateAddress("8 W Cerritos Ave #54") == True
    assert validateAddress("9 Elm St, Apt (B)") == True


def testInvalidAddresses():
    """Tests addresses that should fail validation"""

    assert validateAddress("123 Address St!") == False
    assert validateAddress("123 Address St*") == False
    assert validateAddress("") == False


def testValidCities():
    """Tests city names that should pass validation"""

    assert validateCity("City") == True
    assert validateCity("St. Louis") == True
    assert validateCity("Coeur d'Alene") == True
    assert validateCity("Winston-Salem") == True


def testInvalidCities():
    """Tests city names that should fail validation"""

    assert validateCity("City@Name") == False
    assert validateCity("City Name!") == False
    assert validateCity("") == False


def testValidStates():
    """Tests state abbreviations that should pass validation"""

    assert validateState("PA") == True
    assert validateState("AL") == True
    assert validateState("WY") == True


def testInvalidStates():
    """Tests state values that should fail validation"""

    assert validateState("pa") == False
    assert validateState("Pennsylvania") == False
    assert validateState("") == False


def testStatesNotAllowedAreRejected():
    """Tests that abbreviations outside the fifty accepted values are rejected"""

    assert validateState("PR") == False
    assert validateState("GU") == False
    assert validateState("ZZ") == False


def testValidZipFormat():
    """Tests ZIP codes that should pass validation"""

    assert validateZip("8014") == True
    assert validateZip("15601") == True


def testInvalidZipFormat():
    """Tests ZIP codes that should fail validation"""

    assert validateZip("123") == False
    assert validateZip("156011") == False
    assert validateZip("1560A") == False
    assert validateZip("15601-2201") == False
    assert validateZip("") == False


def testValidPhoneFormat():
    """Tests phone numbers that should pass validation"""

    assert validatePhone("5555550100") == True
    assert validatePhone("555-555-0100") == True
    assert validatePhone("555.555.0100") == True


def testInvalidPhoneFormat():
    """Tests phone numbers that should fail validation"""

    assert validatePhone("555555010") == False
    assert validatePhone("55555501000") == False
    assert validatePhone("(555) 555-0100") == False
    assert validatePhone("555-555-010x") == False
    assert validatePhone("") == False


def testValidEmails():
    """Tests email addresses that should pass validation"""

    assert validateEmail("test@email.com") == True
    assert validateEmail("first_last@email.org") == True
    assert validateEmail("first.last-name+tag@email.net") == True


def testInvalidEmails():
    """Tests email addresses that should fail validation"""

    assert validateEmail("test address@email.com") == False
    assert validateEmail("test@email!com") == False
    assert validateEmail("") == False


def testFieldLength():
    """Tests the database column length guard"""

    assert validateFieldLength("FirstName LastName", 50) == True
    assert validateFieldLength("A" * 50, 50) == True
    assert validateFieldLength("A" * 51, 50) == False


def testValidRecordPasses(valid_record):
    """Tests that a clean record reports no failed fields"""

    assert validateRecord(valid_record) == []


def testRecordReportsBadState(valid_record):
    """Tests that a record with a bad state reports only that field"""

    valid_record["state"] = "ZZ"
    assert validateRecord(valid_record) == ["state"]


def testRecordAllowsEmptyOptionalFields(valid_record):
    """Tests that blank optional fields do not fail the record"""

    valid_record["secondary_phone"] = ""
    valid_record["email_address"] = ""
    assert validateRecord(valid_record) == []


def testRecordReportsMultipleFailures(valid_record):
    """Tests that every failing field is reported"""

    valid_record["state"] = "ZZ"
    valid_record["zip"] = "ABC"
    assert validateRecord(valid_record) == ["state", "zip"]