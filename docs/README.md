## Field Names

The source file and the database tables name the same data differently. Source names are converted to the database column names at parse time so every function after the parser uses one set of names.

first_name to f_name, last_name to l_name, company_name to company, phone1 to primary_phone, phone2 to secondary_phone, email to email_address.

County has no column in the database tables. It stays in memory because the CSV export needs it.

## Validation

Validators check whether a value is acceptable. They do not correct anything. Fixing case or trimming spaces belongs to the cleaning step, which runs first.

Optional fields are only validated when they hold a value, since those columns
accept NULL.

## Duplicates

Duplicates are the same person under a shortened first name, so whole records never match exactly. Records are matched on email address, falling back to the primary phone when there is no email.

Matches are merged rather than discarded. Blank fields are filled from the other
record and the longer first name is kept.

Merging runs before validation so a blank required field can be filled from the matching record before that record is judged.

## 60% Project Milestone

At this milestone, the application supports:

1. Importing a new customer data file
2. Showing records from either database table
3. Adding a record to both database tables
6. Quitting the application

Editing and deleting records remain for the final submission.

## Exports and Backups

  A successful import creates `customer_phone.json` containing first names and phone
  numbers, and `customer_location.csv` containing first name, last name, county, and
  state.

  Existing output files are copied to `.copy` files before being overwritten. The original
  import file is never modified.

## Database

  ### Database Login

  The application prompts for a database username and password when it starts.
  If the connection fails, the user can re-enter the credentials without
  restarting the program.

  For testing, the default project user is:

  - Username: `it412_user`
  - Password: `12345Password`

  These credentials are intended only for the project’s local testing
  environment.

  The default user has SELECT, INSERT, UPDATE, and DELETE privileges on the
  `python_projects` database. The password is entered at runtime and is not
  stored in the Python code.

  ### Database Operations

  Queries use parameters, and inserts use commit and rollback handling.

  Importing fully refreshes `crm_data` and `Mailings`. The supplied file
  produces 493 accepted records in each table. Option 3 adds a validated record
  to both tables as one transaction.

  ## Testing

  Duplicate matching now uses either email address or primary phone number. Malformed rows
  are reported as rejected instead of being silently skipped.

  Import, validation, duplicate, export, and backup behavior are tested with unittest and
  pytest. At this milestone, all 94 tests pass.


  ## Final Project Completion

  The remaining customer database functions were completed.

  4. Editing allows the user to choose a database table, select a record by its ID, choose an editable field, and enter a
     validated replacement value.

  5. Deleting allows the user to choose a database table and record. The user must confirm the deletion before the record is
     removed.

  Table names, primary key columns, and editable fields are limited to approved values before being included in a query. User-
  entered values are passed to the database using query parameters.

  Updates and deletions use commit and rollback handling. If a database operation fails, the transaction is rolled back and the
  user receives an error message.

  The customer function module was reorganized so that the editing and deleting functions are available to the main
  application. Indentation inside the customer record prompt was also corrected for consistency.

  Customer database tests were added using both unittest and Pytest. The tests use mock database objects to verify table
  clearing, bulk loading, record display, inserts, updates, deletions, commits, rollbacks, and deletion confirmation without
  changing the live database.