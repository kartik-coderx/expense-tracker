import streamlit as st
from utils import add_expense, read_expenses

st.set_page_config(page_title="Expense Tracker", page_icon="💰")
st.title("💸 Expense Tracker Web App")

# Input Form
st.subheader("Add New Expense")
with st.form("expense_form"):
    category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Others"])
    amount = st.number_input("Amount", min_value=0.0, step=1.0)
    note = st.text_input("Note (optional)")
    submitted = st.form_submit_button("Add Expense")
    if submitted:
        add_expense(category, amount, note)
        st.success("Expense added successfully!")

# Display Table
st.subheader("📋 All Expenses")
expenses = read_expenses()
if expenses:
    st.dataframe(expenses, use_container_width=True)
else:
    st.info("No expenses added yet.")
