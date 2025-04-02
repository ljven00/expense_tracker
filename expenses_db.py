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
