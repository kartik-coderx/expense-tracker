from utils import add_expense, read_expenses

def main():
    while True:
        print("\n===== Expense Tracker =====")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            category = input("Enter category (e.g., food, travel): ")
            amount = input("Enter amount: ")
            note = input("Enter note (optional): ")
            add_expense(category, amount, note)
            print("✅ Expense added!")

        elif choice == '2':
            expenses = read_expenses()
            if not expenses:
                print("📭 No expenses found!")
            else:
                print("\n{:<12} {:<12} {:<8} {:<20}".format("Date", "Category", "Amount", "Note"))#{:<12}means left aligned with 12 spaces
                print("-" * 60)
                for e in expenses:
                    print("{:<12} {:<12} {:<8} {:<20}".format(e[0], e[1], e[2], e[3]))



        elif choice == '3':
            print("👋 Exiting... Goodbye!")
            break

        else:
            print("❌ Invalid choice. Try again.")

if __name__ == "__main__":
    main()
