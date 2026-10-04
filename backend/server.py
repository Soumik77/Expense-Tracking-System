from datetime import date
from decimal import Decimal
from typing import Literal

import mysql.connector
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend import db_helper
from backend.config import DatabaseConfigurationError
from backend.logging_setup import setup_logger

app = FastAPI(title="Expense Tracking API")
logger = setup_logger(__name__)


class Expense(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    category: Literal["Rent", "Food", "Shopping", "Entertainment", "Other"]
    notes: str = Field(default="", max_length=500)


class DateRange(BaseModel):
    start_date: date
    end_date: date

    @model_validator(mode="after")
    def check_date_order(self):
        if self.start_date > self.end_date:
            raise ValueError("Start date must be on or before end date.")
        return self


@app.exception_handler(mysql.connector.Error)
@app.exception_handler(DatabaseConfigurationError)
async def database_error_handler(request: Request, exc: Exception):
    # Driver errors can contain connection details. Do not return or log them.
    logger.error("Database operation failed (%s)", type(exc).__name__)
    return JSONResponse(
        status_code=503,
        content={"detail": "The database request could not be completed."},
    )


@app.get("/expenses/{expense_date}", response_model=list[Expense])
def get_expenses(expense_date: date):
    return db_helper.fetch_expenses_for_date(expense_date)


@app.post("/expenses/{expense_date}")
def add_or_update_expense(expense_date: date, expenses: list[Expense]):
    db_helper.replace_expenses_for_date(
        expense_date, [expense.model_dump() for expense in expenses]
    )
    return {"message": "Expenses updated successfully"}


@app.post("/analytics/")
def get_analytics(date_range: DateRange):
    data = db_helper.fetch_expense_summary(date_range.start_date, date_range.end_date)
    total = sum(row["total"] for row in data)
    return {
        row["category"]: {
            "total": row["total"],
            "percentage": float(row["total"] / total * 100) if total else 0,
        }
        for row in data
    }


@app.get("/summary/")
def get_analytics_by_months():
    return db_helper.fetch_expense_by_month()
