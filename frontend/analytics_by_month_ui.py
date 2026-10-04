import pandas as pd
import streamlit as st

from frontend.api_client import ApiError, request_api


def analytics_by_month_tab():
    st.subheader("Expense breakdown by month")
    try:
        response = request_api("GET", "/summary/")
    except ApiError as exc:
        st.error(str(exc))
        return
    if not response:
        st.info("No expenses have been recorded yet.")
        return
    data = pd.DataFrame([
        {"Month": row["month"], "Total": float(row["total_expense"])}
        for row in response
    ]).sort_values("Month")
    st.bar_chart(data.set_index("Month")["Total"])
    st.table(data)
