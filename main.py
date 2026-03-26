from database import init_db
from utils import add_expense, read_expenses

def main():
    print("Initializing DB...")
    init_db()
    print("DB Ready ✅")
    while True:
        print("\n==== Expense Tracker ====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            category = input("Category: ")
            amount = input("Amount: ")
            note = input("Note: ")

            add_expense(category, amount, note)
            print("✅ Saved successfully!")

        elif choice == "2":
            expenses = read_expenses()

            if not expenses:
                print("❌ No data found")
            else:
                print("\nDate       Category     Amount     Note")
                print("-------------------------------------------")
                for e in expenses:
                    print(f"{e[0]:<10} {e[1]:<12} {e[2]:<10} {e[3]}")

        elif choice == "3":
            break

        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()