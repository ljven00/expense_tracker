import psycopg2
import sqlite3
from pandas import read_sql
from dotenv import load_dotenv
from os import getenv
from sys import argv

global USE_SQLITE
USE_SQLITE = len(argv) == 2 and argv[1] == "s"

