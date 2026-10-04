from contextlib import contextmanager

import mysql.connector

from backend.config import get_db_config
from backend.logging_setup import setup_logger

logger = setup_logger(__name__)


@contextmanager
def get_db_cursor(commit=False):
    connection = mysql.connector.connect(**get_db_config())
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        yield cursor
        if commit:
            connection.commit()
    except Exception:
        if commit:
            connection.rollback()
        raise
    finally:
        try:
            if cursor is not None:
                cursor.close()
        finally:
            connection.close()


def fetch_all_records():
    with get_db_cursor() as cursor:
        cursor.execute("SELECT * FROM expenses ORDER BY expense_date, id")
        return cursor.fetchall()


def insert_expense(expense_date, amount, category, notes):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "INSERT INTO expenses (expense_date, amount, category, notes) "
            "VALUES (%s, %s, %s, %s)",
            (expense_date, amount, category, notes),
        )


def delete_expenses_for_date(expense_date):
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))


def replace_expenses_for_date(expense_date, expenses):
    """Replace one day's records in one transaction, including an empty list."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s", (expense_date,))
        if expenses:
            cursor.executemany(
                "INSERT INTO expenses (expense_date, amount, category, notes) "
                "VALUES (%s, %s, %s, %s)",
                [
                    (expense_date, expense["amount"], expense["category"], expense["notes"])
                    for expense in expenses
                ],
            )
    logger.info("Expense replacement committed")


def fetch_expenses_for_date(expense_date):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT * FROM expenses WHERE expense_date = %s ORDER BY id", (expense_date,)
        )
        return cursor.fetchall()


def fetch_expense_summary(start_date, end_date):
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT category, SUM(amount) AS total FROM expenses "
            "WHERE expense_date BETWEEN %s AND %s GROUP BY category ORDER BY category",
            (start_date, end_date),
        )
        return cursor.fetchall()


def fetch_expense_by_month():
    with get_db_cursor() as cursor:
        cursor.execute(
            "SELECT DATE_FORMAT(expense_date, '%Y-%m') AS month, "
            "SUM(amount) AS total_expense FROM expenses "
            "GROUP BY DATE_FORMAT(expense_date, '%Y-%m') ORDER BY month"
        )
        return cursor.fetchall()
