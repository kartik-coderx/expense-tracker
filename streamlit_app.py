import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd
import plotly.express as px

# ---------------- Database Config ----------------
DB_PATH = "expense_tracker.db"


def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password_hash TEXT NOT NULL,
        created_at TEXT
    )
    """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        date TEXT,
        category TEXT,
        amount REAL,
        note TEXT
    )
    """)
    conn.commit()
    conn.close()


import bcrypt

# -------- Password Security (bcrypt) --------
def hash_password(password: str):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, stored_hash: str):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
    except:
        return False

# ---------------- Auth Helpers ----------------
def register_user(username: str, password: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username = ?", (username,))
    if c.fetchone():
        conn.close()
        return False, "Username already exists"
    pw_hash = hash_password(password)
    created_at = datetime.now().isoformat()
    c.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
              (username, pw_hash, created_at))
    conn.commit()
    conn.close()
    return True, "User registered successfully"


def verify_user(username: str, password: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    stored_hash = row[0]
    return verify_password(password, stored_hash)


# ---------------- Expense Helpers ----------------

def add_expense(username, date, category, amount, note):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO expenses (username, date, category, amount, note) VALUES (?, ?, ?, ?, ?)",
              (username, date, category, amount, note))
    conn.commit()
    conn.close()


def get_expenses_for_user(username):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, date, category, amount, note FROM expenses WHERE username = ? ORDER BY date DESC", (username,))
    rows = c.fetchall()
    conn.close()
    df = pd.DataFrame(rows, columns=["id", "date", "category", "amount", "note"]) if rows else pd.DataFrame(columns=["id", "date", "category", "amount", "note"])
    return df


def update_expense(expense_id, date, category, amount, note):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE expenses SET date = ?, category = ?, amount = ?, note = ? WHERE id = ?",
              (date, category, amount, note, expense_id))
    conn.commit()
    conn.close()


def delete_expense(expense_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()


# ---------------- Initialize DB ----------------
init_db()


# ---------------- Session Setup ----------------
if "page" not in st.session_state:
    st.session_state.page = "home"
if "user" not in st.session_state:
    st.session_state.user = None


# ---------------- Page Config ----------------
st.set_page_config(page_title="Expense Tracker", layout="wide")

# ---------------- Home Page ----------------
if st.session_state.page == "home":
    st.markdown("<h1 style='text-align:center;'>💸 Expense Tracker</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align:center;color:gray;'>A beautiful and secure way to manage your daily expenses</h4>", unsafe_allow_html=True)
    st.write("")
    if st.button("Get Started →", use_container_width=True):
        st.session_state.page = "auth"
        st.rerun()


# ---------------- Auth Page ----------------
elif st.session_state.page == "auth":
    st.header("Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if verify_user(username, password):
                st.session_state.user = username
                st.session_state.page = "dashboard"
                st.rerun()
            else:
                st.error("Invalid username or password")

    with tab2:
        new_user = st.text_input("Choose a username")
        new_pass = st.text_input("Choose a password", type="password")
        confirm_pass = st.text_input("Confirm password", type="password")
        if st.button("Register"):
            if not new_user or not new_pass:
                st.error("Username and password required")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                ok, msg = register_user(new_user, new_pass)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

    if st.button("← Back", use_container_width=True):
        st.session_state.page = "home"
        st.rerun()


# ---------------- Dashboard ----------------
elif st.session_state.page == "dashboard":
    if not st.session_state.user:
        st.warning("Please login first")
        if st.button("Go to login"):
            st.session_state.page = "auth"
            st.rerun()

    st.markdown(f"<h2>Welcome, {st.session_state.user}</h2>", unsafe_allow_html=True)
    if st.button("Logout"):
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    df = get_expenses_for_user(st.session_state.user)

    # ---- Stats ----
    if not df.empty:
        total = df['amount'].sum()
        avg = df['amount'].mean()
        count = len(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Spend", f"₹ {total:,.2f}")
        col2.metric("Transactions", count)
        col3.metric("Average Spend", f"₹ {avg:,.2f}")

    st.write("---")

    # ---- Add Expense Form ----
    with st.expander("Add Expense", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Date", value=datetime.now())
            category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"])
        with col2:
            amount = st.number_input("Amount", min_value=0.0, format="%f")
            note = st.text_input("Note")
        if st.button("Add Expense", use_container_width=True):
            add_expense(st.session_state.user, date.isoformat(), category, float(amount), note)
            st.success("Expense added")
            st.rerun()

    st.write("---")

    # ---- Table ----
    if df.empty:
        st.info("No expenses found. Start by adding a new expense!")
    else:
        st.subheader("Expenses")
        st.dataframe(df, use_container_width=True)

        # ---- Charts ----
        st.subheader("Visual Insights")
        colA, colB = st.columns(2)
        with colA:
            fig = px.pie(df, names="category", values="amount", title="Category Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        with colB:
            fig2 = px.bar(df, x="date", y="amount", title="Daily Spending")
            st.plotly_chart(fig2, use_container_width=True)

        # ---- CRUD ----
        st.subheader("Edit / Delete")
        for i, row in df.iterrows():
            with st.expander(f"{row['date']} | {row['category']} | ₹{row['amount']}"):
                new_date = st.date_input("Date", value=pd.to_datetime(row['date']), key=f"d_{row['id']}")
                new_cat = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"], index=["Food", "Transport", "Shopping", "Bills", "Other"].index(row['category']), key=f"c_{row['id']}")
                new_amt = st.number_input("Amount", value=row['amount'], key=f"a_{row['id']}")
                new_note = st.text_input("Note", value=row['note'], key=f"n_{row['id']}")

                colu, cold = st.columns(2)
                with colu:
                    if st.button("Update", key=f"u_{row['id']}"):
                        update_expense(row['id'], new_date.isoformat(), new_cat, float(new_amt), new_note)
                        st.success("Updated")
                        st.rerun()
                with cold:
                    if st.button("Delete", key=f"del_{row['id']}"):
                        delete_expense(row['id'])
                        st.warning("Deleted")
                        st.rerun()

        csv = df.to_csv(index=False)
        st.download_button("Download data as CSV", csv, file_name=f"expenses_{st.session_state.user}.csv")

else:
    st.info("Unknown page. Returning to home.")
    st.session_state.page = "home"
    st.rerun()
