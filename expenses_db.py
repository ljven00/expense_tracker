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
