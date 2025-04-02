import psycopg2
import sqlite3
from pandas import read_sql
from dotenv import load_dotenv
from os import getenv
from sys import argv

global USE_SQLITE
USE_SQLITE = len(argv) == 2 and argv[1] == "s"


class ExpenseDB:
    """This class allows to connect to the expenses database
    and perform operation like add, update, delete, and retrieve
    expenses"""
    def __init__(self, use_sqlite=False):
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

    def execute_query(self, query, params=None, fetch=False):
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
