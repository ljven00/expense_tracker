from sys import argv, exit
from os.path import isfile
from os import getenv
from expenses_db import ExpenseDB
from dotenv import load_dotenv
import sqlite3
import psycopg2


def main():
    print("""
    Welcome to the Expense Tracker CLI!

    Usage:
    - Log a new expense:
      python expense_tracker.py log <amount> <category> <description>
    - Update an expense:
      python expense_tracker.py update <id> <amount|None> <category|None> <description|None>
    - Delete an expense:
      python expense_tracker.py delete <id>
    - Analyze expenses with optional filters:
      python expense_tracker.py analyze [--year <year>] [--month <month>] [--category <category>]

    """)

    if len(argv) < 2:
        print("Error: No command provided. Please refer to the usage instructions above.")
        exit(1)

    command = argv[1]

    if isfile(".env"):
        load_dotenv()
        if not all([getenv('DB_NAME'), getenv('DB_USER'), getenv('DB_PASSWORD'), getenv('DB_HOST')]):
            print("-" * 60)
            print("""Incorrect format for .env file. Should be:
                DB_NAME=database_name
                DB_USER=your_username
                DB_PASSWORD=user_password
                DB_HOST=host""")
            exit(1)
        else:
            ExpenseDB.USE_SQLITE = False
    else:
        print("""No .env file for database credentials found.
                SQLite will be used instead of PostgreSQL
            """)
        ExpenseDB.USE_SQLITE = True

    expenses_db = ExpenseDB()
    expenses_db.create_table()

    match command:
        case "log" if len(argv) == 5:
            try:
                amount = float(argv[2])
                category = argv[3]
                description = argv[4]
                expenses_db.add_expense(amount, category, description)
                print("Expense logged successfully.")
            except ValueError:
                print("Invalid amount. Please enter a valid number.")
            except (sqlite3.Error, psycopg2.Error):
                print("Failed to log expense.")

        case "update" if len(argv) >= 4:
            try:
                expense_id = int(argv[2])
                amount = None if argv[3] == 'None' else float(argv[3])
                category = None if argv[4] == 'None' else argv[4]
                description = None if argv[5] == 'None' else argv[5]
                expenses_db.update_expense(expense_id, amount, category, description)
                print("Expense updated successfully.")
            except ValueError:
                print("Invalid input. Please check the parameters.")
            except (sqlite3.Error, psycopg2.Error):
                print("Failed to update expense.")

        case "delete" if len(argv) == 3:
            try:
                expense_id = int(argv[2])
                expenses_db.delete_expense(expense_id)
                print("Expense deleted successfully.")
            except ValueError:
                print("Invalid expense ID. Please enter a valid number.")
            except (sqlite3.Error, psycopg2.Error):
                print("Failed to delete expense.")

        case "analyze":
            filters = {
                "year": None,
                "month": None,
                "category": None}
            args = argv[2:]

            try:
                filter_keys = {
                    "--year": "year",
                    "--month": "month",
                    "--category": "category"}

                for i in range(len(args) - 1):  # Avoid out-of-bounds error
                    if args[i] in filter_keys:
                        key = filter_keys[args[i]]
                        filters[key] = int(args[i + 1]) if key in {"year", "month"} else args[i + 1]
            except (IndexError, ValueError):
                print("Invalid filter format. Use --year <year>, --month <month>, --category <category>.")

            expenses_db.analyze(filters["category"], filters["year"], filters["month"])

        case _:
            print("Invalid command or insufficient arguments. Please refer to the usage instructions above.")
            exit(1)


if __name__ == "__main__":
    main()
