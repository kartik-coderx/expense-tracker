from database import get_connection
from datetime import datetime

def add_expense(category, amount, note):
    conn = get_connection()
    cursor = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date, category, float(amount), note)
    )

    conn.commit()   # 🔥 VERY IMPORTANT
    conn.close()


def read_expenses():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT date, category, amount, note FROM expenses")
    data = cursor.fetchall()

    conn.close()
    return data