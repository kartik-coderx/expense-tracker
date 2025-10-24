import streamlit as st
import sqlite3
import hashlib
from datetime import datetime
import pandas as pd

# --------- Database helpers ---------
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

def hash_password(username, password):
    s = (username + password).encode("utf-8")
    return hashlib.sha256(s).hexdigest()

def register_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
                  (username, hash_password(username, password), datetime.now().isoformat()))
        conn.commit()
        return True, "Registration successful"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    finally:
        conn.close()

def verify_user(username, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        return False
    return row[0] == hash_password(username, password)

# --------- Expense helpers ---------

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
    df = pd.DataFrame(rows, columns=["id", "date", "category", "amount", "note"]) if rows else pd.DataFrame(columns=["id","date","category","amount","note"])
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

# --------- Streamlit app UI ---------

init_db()

if "page" not in st.session_state:
    st.session_state.page = "home"

if "user" not in st.session_state:
    st.session_state.user = None

if "next_clicked" not in st.session_state:
    st.session_state.next_clicked = False

st.set_page_config(page_title="Expense Tracker", layout="centered")

# ---------- Home Page ----------
if st.session_state.page == "home":
    st.session_state.next_clicked = False  # reset next click flag
    st.title("Expense Tracker")
    st.write(
        """
        **Ye web app ek simple Expense Tracker hai.**

        - Isse aap apne daily expenses add aur track kar sakte hain.
        - Kaise kaam karta hai: pehle aap register/login karenge; uske baad aap date, category, amount aur note daal kar expense add kar sakte hain.
        - Aap apne sare expenses ko list me dekh sakte hain aur total amount ka bhi overview mil jayega.
        """
    )
    st.write("")
    if st.button("Aage badho (Next)") and not st.session_state.next_clicked:
        st.session_state.next_clicked = True
        st.session_state.page = "auth"
        st.stop()

# ---------- Auth Page (Login / Register) ----------
elif st.session_state.page == "auth":
    st.header("Login / Register")
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.subheader("Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", key="login_btn"):
            if verify_user(username, password):
                st.session_state.user = username
                st.session_state.page = "dashboard"
                st.success("Login successful")
                st.stop()
            else:
                st.error("Invalid username or password")

    with tab2:
        st.subheader("Register")
        new_user = st.text_input("Choose a username", key="reg_user")
        new_pass = st.text_input("Choose a password", type="password", key="reg_pass")
        confirm_pass = st.text_input("Confirm password", type="password", key="reg_confirm")
        if st.button("Register", key="reg_btn"):
            if not new_user or not new_pass:
                st.error("Username and password required")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match")
            else:
                ok, msg = register_user(new_user, new_pass)
                if ok:
                    st.success(msg + ". Ab login karo.")
                else:
                    st.error(msg)

    if st.button("Back to Home"):
        st.session_state.page = "home"
        st.stop()

# ---------- Dashboard / Expenses Page ----------
elif st.session_state.page == "dashboard":
    if not st.session_state.user:
        st.warning("Pehle login karein.")
        if st.button("Login page par jao"):
            st.session_state.page = "auth"
            st.stop()
    else:
        st.header(f"Welcome, {st.session_state.user}")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "home"
            st.stop()

        with st.expander("Add Expense"):
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
                category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"]) 
            with col2:
                amount = st.number_input("Amount", min_value=0.0, format="%f")
                note = st.text_input("Note (optional)")

            if st.button("Add Expense"):
                add_expense(st.session_state.user, date.isoformat(), category, float(amount), note)
                st.success("Expense added")

        st.write("---")
        df = get_expenses_for_user(st.session_state.user)
        if df.empty:
            st.info("Koi expense nahi mila. Pehle kuch add karo.")
        else:
            total = df['amount'].sum()
            st.write(f"Total expenses: {total}")

            # Edit / Delete functionality
            for index, row in df.iterrows():
                with st.expander(f"{row['date']} | {row['category']} | {row['amount']}"):
                    new_date = st.date_input("Date", value=pd.to_datetime(row['date']), key=f"date_{row['id']}")
                    new_category = st.selectbox("Category", ["Food", "Transport", "Shopping", "Bills", "Other"], index=["Food", "Transport", "Shopping", "Bills", "Other"].index(row['category']), key=f"cat_{row['id']}")
                    new_amount = st.number_input("Amount", value=row['amount'], min_value=0.0, format="%f", key=f"amt_{row['id']}")
                    new_note = st.text_input("Note", value=row['note'], key=f"note_{row['id']}")
                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("Update", key=f"update_{row['id']}"):
                            update_expense(row['id'], new_date.isoformat(), new_category, float(new_amount), new_note)
                            st.success("Expense updated")
                            st.stop()  # <-- safe re-render
                    with col_del:
                        if st.button("Delete", key=f"delete_{row['id']}"):
                            delete_expense(row['id'])
                            st.warning("Expense deleted")
                            st.stop()  # <-- safe re-render

        # export
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button("Download CSV", csv, file_name=f"expenses_{st.session_state.user}.csv")

else:
    st.write("Unknown page. Resetting to home.")
    st.session_state.page = "home"
    st.stop()
