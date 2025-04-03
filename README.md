# 🧾 Expense Tracker CLI

A command-line application for logging, updating, deleting, and analyzing your personal expenses using either PostgreSQL (with `.env`) or SQLite as a fallback.

---

## 🚀 Features

- ✅ Log new expenses
- ✏️ Update existing records
- ❌ Delete expenses
- 📊 Analyze expenses with optional filters
- 💾 Automatic database fallback to SQLite if no `.env` file is found

---

## 📦 Requirements

- Python 3.10+
- [Pipenv](https://pipenv.pypa.io/en/latest/) or `pip`
- Dependencies:
  - `psycopg2-binary`
  - `python-dotenv`
  - `sqlite3` (built-in)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ⚙️ .env Configuration (Optional for PostgreSQL)

If you want to use **PostgreSQL**, create a `.env` file in the root directory:

```env
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password
DB_HOST=your_host
```

If `.env` is not found or incomplete, SQLite will be used instead.

---

## 🛠️ Usage

```bash
python expense_tracker.py <command> [arguments]
```

### Commands

#### 🧾 Log a New Expense

```bash
python expense_tracker.py log <amount> <category> <description>
```

Example:

```bash
python expense_tracker.py log 10.99 groceries "Bought milk and bread"
```

---

#### ✏️ Update an Expense

```bash
python expense_tracker.py update <id> <amount|None> <category|None> <description|None>
```

Use `None` to skip updating a field.

Example:

```bash
python expense_tracker.py update 1 12.50 None "Updated description"
```

---

#### ❌ Delete an Expense

```bash
python expense_tracker.py delete <id>
```

Example:

```bash
python expense_tracker.py delete 1
```

---

#### 📊 Analyze Expenses

```bash
python expense_tracker.py analyze [--year <year>] [--month <month>] [--category <category>]
```

Filters are optional and can be combined.

Examples:

```bash
# Analyze all expenses
python expense_tracker.py analyze

# Analyze by year
python expense_tracker.py analyze --year 2024

# Analyze by category
python expense_tracker.py analyze --category groceries

# Analyze by year and month
python expense_tracker.py analyze --year 2024 --month 3
```

---

## 🧠 Tip

Run the script without any arguments to see the help message and usage guide.

## 🚀 Upcoming Features

- Line graph to track expenses over time
- Box Plot or Bar Graph to compare expenses among different categories