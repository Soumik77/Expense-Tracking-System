import sys

import mysql.connector
from django.db import connection
from contextlib import contextmanager

from django.db.backends.signals import connection_created
from django.db.transaction import commit
from logging_setup import setup_logger

logger = setup_logger('db_helper','server.log')

#Create a connection from the server
@contextmanager
def get_db_cursor(commit = False):
    connection = mysql.connector.connect(
        host='127.0.0.1',
        user='root',
        password='Megha123?',
        database='expense_manager'
    )
    # if connection.is_connected():
    #     print("Connection successfully")
    # else:
    #     print("Failed in connecting to a database")

    # create a cursor where we can fetch data
    cursor = connection.cursor(dictionary=True)
    yield  cursor


    #Commit basically is used to update the database done
    if commit == True:
        connection.commit() #It is basically used to commit the structure
    cursor.close()
    connection.close()


def fetch_all_records():
    # cursor = get_db_cursor() #Filter out the data from the database
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM expenses;')
        expenses = cursor.fetchall()  # Fetch All the data


def insert_expense(expense_date, amount, category, notes):
    logger.info(f'insert_expense_for_date called with date: {expense_date}, amount: {amount}, category: {category}, notes: {notes}')
    with get_db_cursor(commit = True) as cursor:
        cursor.execute("INSERT INTO expenses (expense_date, amount, category, notes) VALUES (%s, %s, %s, %s)",
                       (expense_date,amount, category, notes)
                       )

def delete_expenses_for_date(expense_date):
    logger.info(f'delete_expense_for_date called with {expense_date}')
    with get_db_cursor(commit= True) as cursor:
        cursor.execute("DELETE FROM expenses WHERE expense_date = %s",
                       (expense_date,))




    # cursor.close()
    # # connection.close()

def fetch_expenses_for_date(expense_date):
    # cursor = get_db_cursor() #Filter out the data from the database
    logger.info(f'fetch_expense_for_date called with {expense_date}')
    with get_db_cursor() as cursor:
        cursor.execute('SELECT * FROM expenses Where expense_date = %s;', (expense_date,))
        expenses = cursor.fetchall()  # Fetch All the data
        return expenses

def fetch_expense_summary(start_date, end_date):
    logger.info(f'fetch_expense_summary called with start date:{start_date}, end date:{end_date}')
    with get_db_cursor(commit=True) as cursor:
        cursor.execute('select category, SUM(amount) as Total from expenses where expense_date between %s and  %s group by category;', (start_date,end_date))
        data = cursor.fetchall()
        return data

def fetch_expense_by_month():
    logger.info(f'fetch expense by month')
    with get_db_cursor(commit= True) as cursor:
        cursor.execute('SELECT  MONTHNAME(expense_date) AS month_name, SUM(amount) AS total_expense FROM expenses GROUP BY YEAR(expense_date), MONTH(expense_date), MONTHNAME(expense_date) ORDER BY YEAR(expense_date), MONTH(expense_date)')
        expense = cursor.fetchall()
        return expense







import os

# Test the data
if __name__ == "__main__":
    expenses =  fetch_expenses_for_date("2024-09-30")
    print(expenses)
    # insert_expense("2024-08-25",40, "Food","Eat tasty samosa chat")
    # delete_expenses_for_date("2024-08-25")

    summary = fetch_expense_summary('2024-08-01','2024-08-05')
    for record in summary:
        print(record)

    su = fetch_expense_by_month()
    print(su)
    # for item in su:
    #     print(item)


















