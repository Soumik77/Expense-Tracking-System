from http.client import HTTPException
from fastapi import FastAPI
from datetime import date
import db_helper
from typing import List
from pydantic import BaseModel

app = FastAPI()  #App object

class  Expense(BaseModel):
    amount: float
    category: str
    notes: str

class DateRange(BaseModel):
    start_date: date
    end_date: date



@app.get("/expenses/{expense_date}", response_model=List[Expense])
def get_expenses(expense_date: date):
    expenses = db_helper.fetch_expenses_for_date(expense_date)
    if expenses is None:
        raise HTTPException(status_code=500,detail="Failed to retrive expense from the database")
    return expenses
    # return f"Received get_expense_request{date}"


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses:List[Expense]):
    db_helper.delete_expenses_for_date(expense_date)
    for expense in expenses:
        db_helper.insert_expense(expense_date, expense.amount, expense.category, expense.notes)

    return {"message": "Expenses updated Successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    if data is None:
        raise HTTPException(status_code=500,detail="Failed to retrive expense summary")
    breakdown = {}
    total = sum([row['Total'] for row in data])
    for row in data:
        percentage = (row['Total']/total)*100 if total !=0 else 0
        breakdown[row['category']] = {
            'total': row['Total'],
            'percentage': percentage
        }
    return breakdown

@app.get("/summary/")
def get_analytics_by_months():
    amount = db_helper.fetch_expense_by_month()
    if amount is None:
        raise HTTPException(status_code=500, detail="Failed to retrive expense from the database")
    return amount









