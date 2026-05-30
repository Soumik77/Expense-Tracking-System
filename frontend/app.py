import streamlit as st
from add_update_ui import add_update_tab
from analytics_ui import add_analytics_tab
from analytics_by_month_ui import analytics_by_month_tab

API_URL = 'http://localhost:8000'
st.title("Expense Management System")

tab1, tab2, tab3 = st.tabs(['Add/Update','Analytics By Category','Analytics By Month'])

#Tab1 frontend here
with tab1:
    add_update_tab()
with tab2:
    add_analytics_tab()
with tab3:
    analytics_by_month_tab()
















#
# expense_dt = st.date_input("Expense Date: ")
# # name = st.number_input("Enter your name")
#
# if expense_dt:
#     st.write(f'Fetching expenses for {expense_dt}')

# df = pd.DataFrame({"Date":["2024-08-01", "2024-08-02", "2024-08-03"], "Amount": [250,134,340]})
#
#
# # Text Elements
# st.header("Streamlit Core Features")
# st.subheader("Text Elements")
# st.text("This is a simple text elements")
#
# #Data Display
# st.subheader("Data Display")
# st.write("Here is a simple table:")
# st.table(df)
#
# #Charts
# st.subheader("Charts")
# st.line_chart([1,2,3,4])
#
# #User input
# st.subheader("User Input")
# value = st.slider("Select a value", 0,100)
# st.write(f'Selected value: {value}')
#
# #CheckBox
# if st.checkbox("Show/Hide"):
#     st.write("Checkbox is checked")
#
# #SelectBox
# option = st.selectbox("Select a number",["Food","Rent"], label_visibility="collapsed")
# st.write(f"You selected:{option}")
#
# #multibox
# options = st.multiselect("Select Multiple numbers:", [1,2,3,4])
# st.write(f"You selected : {options}")

