import unittest
import sqlite3
from finance_manager import (
    register_user, 
    add_transaction, 
    generate_report, 
    initialize_db
)

class TestPersonalFinanceManager(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.conn = sqlite3.connect(":memory:")
        initialize_db(self.conn)  # Initialize the schema

    def tearDown(self):
        self.conn.close()

    def test_register_user_success(self):
        result = register_user(self.conn, "testuser", "password123")
        self.assertEqual(result, "Registration successful!")

    def test_register_user_duplicate(self):
        register_user(self.conn, "testuser", "password123")
        result = register_user(self.conn, "testuser", "newpassword")
        self.assertEqual(result, "Username already exists. Please try again.")

    def test_add_transaction(self):
        user_id = 1
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, "testuser", "password123"))
        self.conn.commit()

        result = add_transaction(self.conn, user_id, "Food", 50.0, "expense")
        self.assertEqual(result, "Transaction added successfully!")

        cursor.execute("SELECT category, amount, type FROM transactions WHERE user_id = ?", (user_id,))
        transactions = cursor.fetchall()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], ("Food", 50.0, "expense"))

    def test_generate_report(self):
        user_id = 1
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (user_id, "testuser", "password123"))
        cursor.execute("INSERT INTO transactions (user_id, category, amount, type, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, "Salary", 1000.0, "income", "2024-11-01"))
        cursor.execute("INSERT INTO transactions (user_id, category, amount, type, date) VALUES (?, ?, ?, ?, ?)",
                       (user_id, "Food", 200.0, "expense", "2024-11-02"))
        self.conn.commit()
        
        report = generate_report(self.conn, user_id, "2024-11")
        self.assertIn("Total Income: 1000.0", report)
        self.assertIn("Total Expenses: 200.0", report)
        self.assertIn("Savings: 800.0", report)

if __name__ == "__main__":
    unittest.main()
