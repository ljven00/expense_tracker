import psycopg2
import sqlite3
import pandas as pd
from dotenv import load_dotenv
from os import getenv


# from sys import argv

# global USE_SQLITE
# USE_SQLITE = len(argv) == 2 and argv[1] == "s"

# Loading environment variable


class ExpenseDB:
    """This class allows to connect to the expenses database
    and perform operation like add, update, delete, and retrieve
    expenses"""

    USE_SQLITE = False

    def __init__(self, use_sqlite=USE_SQLITE):
        """When Initialize the path to the sqlite db is set
            if using SQLite else the Postgres Credentials are loaded"""
        self.use_sqlite = use_sqlite
        self.conn = None
        if self.use_sqlite:
            self.db_path = "expenses"
        else:
            self.dbname = getenv('DB_NAME')
            self.user = getenv('DB_USER')
            self.password = getenv('DB_PASSWORD')
            self.host = getenv('DB_HOST')

    def get_connection(self):
        """Establish a database connection."""
        if not self.conn:
            # Avoid returning different connection object
            try:
                # Connect to SQLite
                if self.use_sqlite:
                    self.conn = sqlite3.connect(self.db_path)
                # Connect to Postgres
                else:
                    self.conn = psycopg2.connect(
                        dbname=self.dbname,
                        user=self.user,
                        password=self.password,
                        host=self.host
                    )
            except (psycopg2.Error, sqlite3.Error) as e:
                print(f"Database connection error: {e}")
                return None
        return self.conn

    def close_connection(self):
        """Close the database connection."""
        # If there is a connection then it is closed
        if self.conn:
            self.conn.close()
            self.conn = None

    def execute_query(self, query: str, params=None, fetch=False):
        """Execute a query using query parameters in case of INSERTING, UPDATING
        If it is a SELECT then fetch is True"""
        conn = self.get_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ())
            # If it is a SELECT then there needs to be a ResultSet
            if fetch:
                results = cursor.fetchall()
                cursor.close()
                return results
            # Commit changes in case any
            conn.commit()
            cursor.close()
        except (psycopg2.Error, sqlite3.Error) as e:
            print(f"Database error: {e}")

    def create_table(self):
        """Create the expenses table if it does not exist."""
        query = (
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                category TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            );
            """
            if self.use_sqlite else
            """
            CREATE TABLE IF NOT EXISTS expenses (
                id SERIAL PRIMARY KEY,
                amount DECIMAL NOT NULL,
                category VARCHAR(20),
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            );
            """
        )
        self.execute_query(query)

    def add_expense(self, amount: float, category: str, description: str):
        """Insert a new expense into the database."""
        query = "INSERT INTO expenses (amount, category, description) VALUES (?, ?, ?)"
        self.execute_query(query, (amount, category, description))
        print("Expense added successfully.")

    def delete_expense(self, expense_id: int):
        """Delete an expense by ID."""
        query = "DELETE FROM expenses WHERE id = ?"
        conn = self.get_connection()
        if conn is None:
            return
        cursor = conn.cursor()
        cursor.execute(query, (expense_id,))
        if cursor.rowcount > 0:
            print(f"Expense with ID {expense_id} deleted successfully.")
        else:
            print(f"No expense found with ID {expense_id}.")
        conn.commit()
        cursor.close()

    def update_expense(self, expense_id: int, amount=None, category=None, description=None):
        """Update an expense based on provided values."""
        updates = []
        params = []
        if amount:
            updates.append("amount = ?")
            params.append(amount)
        if category:
            updates.append("category = ?")
            params.append(category)
        if description is not None:
            updates.append("description = ?")
            params.append(description)
        if not updates:
            print("No update provided.")
            return
        query = f"UPDATE expenses SET {', '.join(updates)} WHERE id = ?"
        params.append(expense_id)
        self.execute_query(query, tuple(params))
        print(f"Expense with ID {expense_id} updated successfully.")

    def fetch_expenses(self):
        """Fetch all expenses and return the Result as a DataFrame."""
        conn = self.get_connection()
        if conn is None:
            return None
        query = "SELECT * FROM expenses"
        df = pd.read_sql(query, conn)
        conn.close()
        return df

    def analyze(self, category_filter=None, year_filter=None, month_filter=None):
        """Analyze expenses with additional features."""
        df = self.fetch_expenses()
        if df is None or df.empty:
            print("No expenses recorded.")
            return

        # Extract year, month, and day from the date column
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day'] = df['date'].dt.day

        # Apply filters
        if category_filter:
            df = df[df['category'].str.lower() == category_filter.lower()]
        if year_filter:
            df = df[df['year'] == int(year_filter)]
        if month_filter:
            df = df[df['month'] == int(month_filter)]

        if df.empty:
            print("No expenses match the given filters.")
            return

        # Apply window functions for grouping by category
        df['category_sum'] = df.groupby('category')['amount'].transform('sum')
        df['category_avg'] = df.groupby('category')['amount'].transform('mean')

        print(df[['id', 'amount', 'category', 'description', 'date', 'year', 'month', 'day', 'category_sum',
                  'category_avg']])
