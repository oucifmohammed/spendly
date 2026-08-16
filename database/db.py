import os
import sqlite3
from datetime import date

from werkzeug.security import generate_password_hash

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "expense_tracker.db")

CATEGORIES = ["Food", "Transport", "Bills", "Health", "Entertainment", "Shopping", "Other"]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()


def seed_db():
    conn = get_db()
    row = conn.execute("SELECT COUNT(*) AS count FROM users").fetchone()
    if row["count"] > 0:
        conn.close()
        return

    password_hash = generate_password_hash("demo123")
    cursor = conn.execute(
        "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
        ("Demo User", "demo@spendly.com", password_hash),
    )
    user_id = cursor.lastrowid

    today = date.today()
    year, month = today.year, today.month

    # (day, amount, category, description) — 8 rows, one per category
    # minimum (Food gets a second entry). Days chosen to be valid in every
    # month, including February.
    sample_expenses = [
        (2, 45.50, "Food", "Grocery shopping"),
        (4, 30.00, "Transport", "Monthly bus pass"),
        (5, 85.00, "Bills", "Electricity bill"),
        (8, 60.00, "Health", "Pharmacy purchase"),
        (10, 22.99, "Entertainment", "Movie tickets"),
        (12, 150.00, "Shopping", "New shoes"),
        (15, 12.75, "Food", "Lunch with coworkers"),
        (18, 18.20, "Other", "Miscellaneous purchase"),
    ]

    for day, amount, category, description in sample_expenses:
        expense_date = date(year, month, day).isoformat()
        conn.execute(
            """INSERT INTO expenses (user_id, amount, category, date, description)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, amount, category, expense_date, description),
        )

    conn.commit()
    conn.close()
