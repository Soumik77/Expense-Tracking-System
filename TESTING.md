# Testing

## Default automated checks

From the project root, after installing `requirement.txt`:

```bash
python -m pytest -q
```

These checks cover:

- A successful replacement commits once.
- Insert and commit failures roll back and close database resources.
- Invalid amounts, categories, notes, and date ranges do not reach the database.
- Database errors return a generic failure response.
- A successful read followed by a failed save never displays success.
- A failed read does not create an empty editable form.
- More than five existing records survive a save.
- Clearing all records requires confirmation in the interface.
- Network errors do not expose raw connection details.

The tests use generated sample values. They do not require a database containing specific personal records.

## Optional live MySQL tests

Use a disposable **local** MySQL 8 server and an explicitly selected testing account. This account needs permission to create and drop databases. The test fixture creates a unique database named `expense_test_<random ID>`, uses the application's InnoDB schema, and drops that same database afterward. It does not select `expense_manager` or load credentials from your application account.

Set these environment variables locally:

```text
RUN_MYSQL_TESTS=1
MYSQL_TEST_HOST=127.0.0.1
MYSQL_TEST_PORT=3306
MYSQL_TEST_USER=your_local_testing_account
MYSQL_TEST_PASSWORD=your_local_testing_password
```

Then run:

```bash
python -m pytest -q -m integration
```

The integration tests verify API save/read/report round trips, rollback when an insert violates the database constraint, separation of months across years, literal handling of SQL-like notes, and preservation of other dates when clearing a day.

Do not commit testing credentials. If a test process is forcibly terminated, its uniquely named temporary database may need to be removed manually.
