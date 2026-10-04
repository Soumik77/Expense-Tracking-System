import streamlit as st

from frontend.add_update_ui import add_update_tab
from frontend.analytics_by_month_ui import analytics_by_month_tab
from frontend.analytics_ui import add_analytics_tab

st.title("Expense Management System")
tab1, tab2, tab3 = st.tabs(["Add/Update", "Analytics By Category", "Analytics By Month"])

with tab1:
    add_update_tab()
with tab2:
    add_analytics_tab()
with tab3:
    analytics_by_month_tab()
