import sqlite3
import bcrypt
from datetime import datetime

# Initialize the database
def initialize_db():
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                type TEXT CHECK(type IN ('income', 'expense')),
                category TEXT,
                amount REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                category TEXT,
                amount REAL NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        conn.commit()

# User Registration
def register_user():
    username = input("Enter a username: ")
    password = input("Enter a password: ")
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    try:
        with sqlite3.connect("finance_manager.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
        print("Registration successful!")
    except sqlite3.IntegrityError:
        print("Username already exists. Please try again.")

# User Authentication
def login_user():
    username = input("Enter your username: ")
    password = input("Enter your password: ")
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        if user and bcrypt.checkpw(password.encode(), user[1]):
            print("Login successful!")
            return user[0]  # Return user ID
        else:
            print("Invalid credentials.")
            return None

# Add Transaction
def add_transaction(user_id):
    transaction_type = input("Enter type (income/expense): ").lower()
    category = input("Enter category (e.g., Food, Rent, Salary): ")
    amount = float(input("Enter amount: "))
    date = input("Enter date (YYYY-MM-DD) or press Enter for today: ") or datetime.now().strftime("%Y-%m-%d")
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO transactions (user_id, type, category, amount, date)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, transaction_type, category, amount, date))
        conn.commit()
    print("Transaction added successfully!")

# Generate Financial Reports
def generate_report(user_id):
    report_type = input("Generate report for (monthly/yearly): ").lower()
    date_filter = input("Enter year (YYYY) and optionally month (YYYY-MM) for filtering: ")
    query = """
        SELECT type, category, SUM(amount) 
        FROM transactions 
        WHERE user_id = ? AND date LIKE ?
        GROUP BY type, category
    """
    filter_value = f"{date_filter}%"  # E.g., '2024%' for yearly, '2024-11%' for monthly
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute(query, (user_id, filter_value))
        results = cursor.fetchall()
        total_income, total_expenses = 0, 0
        print("\nReport:")
        for row in results:
            if row[0] == "income":
                total_income += row[2]
            else:
                total_expenses += row[2]
            print(f"Category: {row[1]}, Type: {row[0]}, Amount: {row[2]:.2f}")
        print(f"Total Income: {total_income:.2f}")
        print(f"Total Expenses: {total_expenses:.2f}")
        print(f"Savings: {total_income - total_expenses:.2f}")

# Set Monthly Budgets
def set_budget(user_id):
    category = input("Enter category for budget: ")
    amount = float(input("Enter budget amount: "))
    with sqlite3.connect("finance_manager.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO budgets (user_id, category, amount) VALUES (?, ?, ?)", 
                       (user_id, category, amount))
        conn.commit()
    print("Budget set successfully!")

# Main Application Menu
def main_menu():
    initialize_db()
    print("Welcome to Personal Finance Manager!")
    while True:
        print("\n1. Register\n2. Login\n3. Exit")
        choice = input("Select an option: ")
        if choice == "1":
            register_user()
        elif choice == "2":
            user_id = login_user()
            if user_id:
                while True:
                    print("\n1. Add Transaction\n2. Generate Report\n3. Set Budget\n4. Logout")
                    user_choice = input("Select an option: ")
                    if user_choice == "1":
                        add_transaction(user_id)
                    elif user_choice == "2":
                        generate_report(user_id)
                    elif user_choice == "3":
                        set_budget(user_id)
                    elif user_choice == "4":
                        break
                    else:
                        print("Invalid option.")
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main_menu()
