import csv
from datetime import datetime

# Save an expense
def add_expense(category, amount, note):
    with open('expenses.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now().strftime('%Y-%m-%d'), category , amount, note])

# Read all expenses
def read_expenses():
    expenses = []
    with open('expenses.csv', mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # skip header
        for row in reader:
            expenses.append(row)
    return expenses
