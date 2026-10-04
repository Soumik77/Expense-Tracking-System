from datetime import date

import pandas as pd
import streamlit as st

from frontend.api_client import ApiError, request_api


def add_analytics_tab():
    today = date.today()
    start_col, end_col = st.columns(2)
    start_date = start_col.date_input("Start date", today.replace(day=1))
    end_date = end_col.date_input("End date", today)

    if st.button("Get analytics"):
        if start_date > end_date:
            st.error("Start date must be on or before end date.")
            return
        try:
            response = request_api("POST", "/analytics/", json={
                "start_date": start_date.isoformat(), "end_date": end_date.isoformat(),
            })
        except ApiError as exc:
            st.error(str(exc))
            return
        if not response:
            st.info("No expenses were found in this date range.")
            return
        data = pd.DataFrame([
            {"Category": category, "Total": float(values["total"]),
             "Percentage": float(values["percentage"])}
            for category, values in response.items()
        ]).sort_values("Percentage", ascending=False)
        st.subheader("Expense breakdown by category")
        st.bar_chart(data.set_index("Category")["Percentage"])
        st.table(data)
