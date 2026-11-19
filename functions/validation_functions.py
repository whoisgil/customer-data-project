# validation functions for the customer data import application

show_debug_information = False


def validateName(passed_name):
    """Validates a first or last name allowing only letters, spaces, single quotes and dashes"""

    allowed_characters = "'- "

    if len(passed_name) == 0:
        return False

    for current_character in passed_name:
        if not current_character.isalpha() and current_character not in allowed_characters:
            return False

    return True


def validateCompany(passed_company):
    """Validates a company name by rejecting a small set of forbidden symbols"""

    forbidden_characters = "~`^{}|<>"

    for current_character in passed_company:
        if current_character in forbidden_characters:
            return False

    return True


def validateAddress(passed_address):
    """Validates a street address allowing letters, numbers, spaces and a few punctuation marks"""

    # the backslash is doubled so Python stores it as one literal character
    allowed_characters = "#,.-&()\\ "

    if len(passed_address) == 0:
        return False

    for current_character in passed_address:
        if not current_character.isalnum() and current_character not in allowed_characters:
            return False

    return True


def validateCity(passed_city):
    """Validates a city name by rejecting a set of forbidden symbols"""

    forbidden_characters = '!"@$%^&*_=+<>?;[]{}~`'

    if len(passed_city) == 0:
        return False

    for current_character in passed_city:
        if current_character in forbidden_characters:
            return False

    return True


def validateState(passed_state):
    """Validates a state abbreviation against the fifty accepted values"""

    valid_states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA",
                    "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD",
                    "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ",
                    "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC",
                    "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]

    # case is not corrected here because that belongs to the cleaning step
    if passed_state in valid_states:
        return True

    return False


def validateZip(passed_zip):
    """Validates a ZIP code by requiring either four or five digits and nothing else"""

    if not passed_zip.isdigit():
        return False

    if len(passed_zip) != 4 and len(passed_zip) != 5:
        return False

    return True


def validatePhone(passed_phone):
    """Validates a phone number as either ten digits or twelve characters with separators"""

    allowed_characters = "-."

    for current_character in passed_phone:
        if not current_character.isdigit() and current_character not in allowed_characters:
            return False

    if passed_phone.isdigit() and len(passed_phone) == 10:
        return True

    # only the length is checked because the separator positions are not specified
    if len(passed_phone) == 12 and not passed_phone.isdigit():
        return True

    return False


def validateEmail(passed_email):
    """Validates an email address allowing letters, numbers and a few punctuation marks"""

    allowed_characters = ".-_@+"

    if len(passed_email) == 0:
        return False

    for current_character in passed_email:
        if not current_character.isalnum() and current_character not in allowed_characters:
            return False

    return True


def validateFieldLength(passed_value, passed_maximum):
    """Checks that a value is short enough to fit inside a database column"""

    # guards the varchar(50) columns and the joined name going into Mailings
    if len(passed_value) > passed_maximum:
        return False

    return True


def validateRecord(passed_record):
    """Validates every field in one customer record and returns a list of the fields that failed"""

    failed_fields = []

    if not validateName(passed_record["f_name"]):
        failed_fields.append("f_name")

    if not validateName(passed_record["l_name"]):
        failed_fields.append("l_name")

    if not validateCompany(passed_record["company"]):
        failed_fields.append("company")

    if not validateAddress(passed_record["address"]):
        failed_fields.append("address")

    if not validateCity(passed_record["city"]):
        failed_fields.append("city")

    if not validateState(passed_record["state"]):
        failed_fields.append("state")

    if not validateZip(passed_record["zip"]):
        failed_fields.append("zip")

    if not validatePhone(passed_record["primary_phone"]):
        failed_fields.append("primary_phone")

    # blank optional fields are skipped because those columns accept NULL
    if len(passed_record["secondary_phone"]) > 0:
        if not validatePhone(passed_record["secondary_phone"]):
            failed_fields.append("secondary_phone")

    if len(passed_record["email_address"]) > 0:
        if not validateEmail(passed_record["email_address"]):
            failed_fields.append("email_address")

    mailing_name = (
      passed_record["f_name"]
      + " "
      + passed_record["l_name"]
  )

    if not validateFieldLength(mailing_name, 50):
      failed_fields.append("mailing_name")

    return failed_fields