# Expense Tracking and Analytics System

A Python learning project for recording daily expenses and reviewing spending by category and month. The application uses a Streamlit interface, a FastAPI backend, and a MySQL database.

## Features

- Add, edit, and remove expense records for a selected date.
- Save all changes for a day in one database transaction.
- Filter category totals by date range and display percentage breakdowns.
- Compare monthly totals, keeping different years separate.
- Validate expense amounts, categories, note lengths, and date ranges.
- Run automated database, API, and interface checks.

## Stack

Python 3.12, MySQL 8, FastAPI, Streamlit, pandas, Pydantic, pytest.

## Local setup

Use a local MySQL 8.0.16 or later server. The schema uses InnoDB transactions and an enforced positive-amount constraint. The commands below assume you are in the project root.

If you downloaded a ZIP of the project, extract it and open a terminal in that folder. Skip the clone and change-directory commands below.

### 1. Install the Python dependencies

```bash
git clone https://github.com/Soumik77/Expense-Tracking-System.git
cd Expense-Tracking-System
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirement.txt
```

On Windows, create the environment with `py -3 -m venv .venv` and activate it in PowerShell with `.venv\Scripts\Activate.ps1`.

### 2. Create the database

Open the MySQL client as a local administrator:

```bash
mysql -u root -p
```

In the MySQL client, run:

```sql
SOURCE database/schema.sql;
CREATE USER 'expense_app'@'127.0.0.1' IDENTIFIED BY 'choose-a-new-local-password';
GRANT SELECT, INSERT, DELETE ON expense_manager.* TO 'expense_app'@'127.0.0.1';
```

Replace the example password locally. Do not reuse a password that was previously committed. If the account already exists, update its password instead of creating it again.

The schema script creates a new table if it is missing. It does not migrate or erase an existing table. Existing installations must have an InnoDB `expenses` table with the columns and constraints shown in `database/schema.sql`. Back up existing data before changing its schema.

Optionally, load synthetic examples into an **empty demo database**, once:

```sql
SOURCE database/sample_data.sql;
```

These examples use August and September 2026. Choose those dates in the interface to view them.

### 3. Configure local credentials

```bash
cp .env.example .env
```

On Windows PowerShell, use `Copy-Item .env.example .env`.

Edit `.env` to set `DB_PASSWORD` to your new local password. The other defaults match the database setup above. The application loads this file automatically; environment variables take precedence. The file is excluded from Git.

### 4. Start both processes

Backend, in one terminal:

```bash
python -m uvicorn backend.server:app --reload --host 127.0.0.1
```

Frontend, in another terminal with the same environment activated:

```bash
python -m streamlit run frontend/app.py --server.address 127.0.0.1
```

Open the interface at http://127.0.0.1:8501. API documentation is at http://127.0.0.1:8000/docs.

## Using the application

- Amounts must be positive and have no more than two decimal places.
- Set an existing amount to zero to remove that row on the next save.
- Clearing every record for a date requires the confirmation checkbox.
- A failed read disables the edit form. A failed save does not display a success message.
- The API replaces a selected day's records as one operation. An empty list clears that day.
- Monthly reports use `YYYY-MM` labels, so the same month in different years stays separate.

This is a local, single-user learning application. It has no authentication or multi-user conflict detection. Keep it bound to localhost when using personal records.

## Tests

```bash
python -m pytest -q
```

The default suite uses mocks for database and HTTP boundaries and runs Streamlit interface checks without a browser. It cannot connect to your personal database. Live MySQL tests are skipped unless explicitly enabled.

See [TESTING.md](TESTING.md) for the optional MySQL integration tests, including rollback after a failed insert.

## Project structure

- `backend/`: API routes, configuration, database queries, and operational logging.
- `frontend/`: Streamlit pages and the API request helper.
- `database/schema.sql`: database and InnoDB table definition.
- `database/sample_data.sql`: synthetic demonstration records.
- `test/`: database, API, interface, and opt-in MySQL tests.
- `.env.example`: configuration template without a password.

## Repository privacy

Passwords belong in `.env`, not source code. Logs, cached Python files, virtual environments, and editor files are excluded from Git. Application logs record operational outcomes without amounts, categories, or notes.

See [SECURITY_CLEANUP.md](SECURITY_CLEANUP.md) for the remaining credential-rotation and Git-history steps after replacing an older checkout.
