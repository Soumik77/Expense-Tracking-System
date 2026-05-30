import streamlit as st
from datetime import date
import requests
import pandas as pd

API_URL = 'http://localhost:8000'

def add_analytics_tab():
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input('Start Date', date(2024, 8, 1))
    with col2:
        end_date = st.date_input("End Date", date(2024, 8, 5))


    if st.button("Get Analytics"):
        payload = {
            "start_date":start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        }
        response = requests.post(f'{API_URL}/analytics',json=payload)
        response = response.json()
        data  = pd.DataFrame({
            "Category":list(response.keys()),
            'Total':[response[category]['total'] for category in response],
            'Percentage': [response[category]['percentage'] for category in response]

        })
        data_sorted = data.sort_values(by='Percentage',ascending=False)
        st.title("Expense Breakdown By Category")
        st.bar_chart(data = data_sorted.set_index("Category")['Percentage'])
        st.table(data_sorted)


