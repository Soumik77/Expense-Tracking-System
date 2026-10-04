from datetime import date

import streamlit as st

from frontend.api_client import ApiError, request_api

CATEGORIES = ["Rent", "Food", "Shopping", "Entertainment", "Other"]


def add_update_tab():
    selected_date = st.date_input("Expense date", date.today())
    try:
        existing_expenses = request_api("GET", f"/expenses/{selected_date}")
    except ApiError as exc:
        st.error(str(exc))
        # An empty editable form after a failed read could overwrite unseen records.
        return

    st.caption("Amounts use two decimal places. Set an amount to zero to remove that row.")
    with st.form(key=f"expense_form_{selected_date}"):
        expenses = []
        # Keep every existing record, even when a day has more than five.
        for i in range(max(5, len(existing_expenses))):
            existing = existing_expenses[i] if i < len(existing_expenses) else {}
            category = existing.get("category", "Shopping")
            categories = CATEGORIES if category in CATEGORIES else [*CATEGORIES, category]
            amount_col, category_col, notes_col = st.columns(3)
            amount = amount_col.number_input(
                "Amount", min_value=0.0, max_value=9999999999.99, step=0.01,
                value=float(existing.get("amount", 0)), format="%.2f",
                key=f"amount_{selected_date}_{i}",
            )
            selected_category = category_col.selectbox(
                "Category", categories, index=categories.index(category),
                key=f"category_{selected_date}_{i}",
            )
            notes = notes_col.text_input(
                "Notes", value=existing.get("notes", ""), max_chars=500,
                key=f"notes_{selected_date}_{i}",
            )
            if amount > 0:
                expenses.append({
                    "amount": f"{amount:.2f}", "category": selected_category, "notes": notes,
                })
        confirm_clear = st.checkbox("Confirm clearing all expenses for this date")
        submitted = st.form_submit_button("Save expenses")

    if submitted:
        if existing_expenses and not expenses and not confirm_clear:
            st.warning("Confirm clearing all expenses before saving an empty day.")
            return
        try:
            request_api("POST", f"/expenses/{selected_date}", json=expenses)
        except ApiError as exc:
            st.error(str(exc))
        else:
            st.success("Expenses updated successfully.")
