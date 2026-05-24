"""
ETL Phase – Extract
Read raw CSV files from the datasets/ folder into pandas DataFrames.
"""

import os
import pandas as pd

DATASETS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "datasets")


def extract_books() -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, "books.csv")
    df = pd.read_csv(path)
    return df


def extract_borrowers() -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, "borrowers.csv")
    df = pd.read_csv(path)
    return df


def extract_transactions() -> pd.DataFrame:
    path = os.path.join(DATASETS_DIR, "transactions.csv")
    df = pd.read_csv(path, parse_dates=["borrow_date", "due_date", "return_date"])
    return df


def extract_all() -> dict:
    """Return all three raw DataFrames keyed by name."""
    books = extract_books()
    borrowers = extract_borrowers()
    transactions = extract_transactions()
    total = len(books) + len(borrowers) + len(transactions)
    return {
        "books": books,
        "borrowers": borrowers,
        "transactions": transactions,
        "total_records": total,
    }
