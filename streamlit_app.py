import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Expense Tracker", layout="centered")
st.title("📊 Personal Expense Tracker")

# User input
username = st.text_input("Enter your name:")

if username:
    os.makedirs("data", exist_ok=True)
    filename = f"data/expenses_{username.lower()}.csv"

    # Load existing data
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        df = pd.DataFrame(columns=["Date", "Category", "Amount", "Description"])

    # Add new expense
    st.subheader("➕ Add Expense")
    with st.form("form"):
        date = st.date_input("Date")
        category = st.selectbox("Category", ["Food", "Travel", "Shopping", "Bills", "Others"])
        amount = st.number_input("Amount", min_value=0.0)
        description = st.text_input("Description")
        add = st.form_submit_button("Add")

    if add:
        new_data = pd.DataFrame([{
            "Date": date,
            "Category": category,
            "Amount": amount,
            "Description": description
        }])
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(filename, index=False)
        st.success("Expense added!")

    # Show expense table
    st.subheader("📜 Your Expenses")
    st.dataframe(df)

    # Summary
    if not df.empty:
        st.subheader("📈 Summary")
        st.write("Total Spent: ₹", df["Amount"].sum())
