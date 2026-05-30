from calendar import month

import streamlit as st
from datetime import date
import requests
import pandas as pd
API_URL = 'http://localhost:8000'


def analytics_by_month_tab():
    st.title("Expense Breakdown By Months")
    response = requests.get(f'{API_URL}/summary/')
    if response.status_code == 200:
        existing_expense = response.json()
    else:
        st.error("Failed to retrieve expenses")
        existing_expense = []
    res = response.json()
    data = pd.DataFrame({
        "Month": [resp['month_name'] for resp in res],
        'Total': [resp['total_expense'] for resp in res]
    })
    data_sorted = data.sort_values(by='Month')
    st.bar_chart(data=data_sorted.set_index("Month")['Total'])
    st.table(data_sorted)





