"""
ETL Phase – Transform
Clean, validate and normalise raw DataFrames before loading.
Steps applied per entity:
  Books     – fill missing category/publisher, drop ISBN duplicates
  Borrowers – fill missing phone, drop email duplicates
  Transactions – parse dates, drop full duplicates, fill missing due_date
"""

import pandas as pd
from datetime import timedelta


# ── Books ────────────────────────────────────────────────────────────────────

def transform_books(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    # Standardise column names
    df.columns = df.columns.str.strip().str.lower()

    # Fill missing category and publisher
    df["category"] = df["category"].fillna("General")
    df["publisher"] = df["publisher"].fillna("Unknown")

    # Fill missing ISBN with a generated placeholder
    mask = df["isbn"].isna() | (df["isbn"].astype(str).str.strip() == "")
    df.loc[mask, "isbn"] = "ISBN-" + df.loc[mask, "book_id"].astype(str)

    # Drop rows with no title or author
    df = df.dropna(subset=["title", "author"])
    df["title"] = df["title"].str.strip()
    df["author"] = df["author"].str.strip()

    # Remove duplicate ISBNs (keep first occurrence)
    df = df.drop_duplicates(subset=["isbn"], keep="first")

    after = len(df)
    print(f"[Transform] Books: {before} -> {after} records ({before - after} removed)")
    return df.reset_index(drop=True)


# ── Borrowers ────────────────────────────────────────────────────────────────

def transform_borrowers(df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    df.columns = df.columns.str.strip().str.lower()

    # Fill missing phone
    df["phone"] = df["phone"].fillna("N/A")
    df["phone"] = df["phone"].astype(str).str.strip()
    df.loc[df["phone"] == "nan", "phone"] = "N/A"

    # Drop rows with no name or email
    df = df.dropna(subset=["borrower_name", "email"])
    df["email"] = df["email"].str.strip().str.lower()

    # Remove duplicate emails (keep first)
    df = df.drop_duplicates(subset=["email"], keep="first")

    # Normalise membership_date
    df["membership_date"] = pd.to_datetime(df["membership_date"], errors="coerce")
    df["membership_date"] = df["membership_date"].fillna(pd.Timestamp("2023-01-01"))

    after = len(df)
    print(f"[Transform] Borrowers: {before} -> {after} records ({before - after} removed)")
    return df.reset_index(drop=True)


# ── Transactions ─────────────────────────────────────────────────────────────

def transform_transactions(df: pd.DataFrame, books_df: pd.DataFrame, borrowers_df: pd.DataFrame) -> pd.DataFrame:
    before = len(df)

    df.columns = df.columns.str.strip().str.lower()

    # Parse dates
    for col in ["borrow_date", "due_date", "return_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Fill missing due_date as borrow_date + 14 days
    mask = df["due_date"].isna()
    df.loc[mask, "due_date"] = df.loc[mask, "borrow_date"] + timedelta(days=14)

    # Drop rows without valid borrow_date
    df = df.dropna(subset=["borrow_date"])

    # Drop full duplicate rows
    df = df.drop_duplicates(keep="first")

    # Keep only book_ids and borrower_ids that exist in transformed datasets
    valid_book_ids = set(books_df["book_id"].astype(int))
    valid_borrower_ids = set(borrowers_df["borrower_id"].astype(int))
    df = df[df["book_id"].isin(valid_book_ids) & df["borrower_id"].isin(valid_borrower_ids)]

    after = len(df)
    print(f"[Transform] Transactions: {before} -> {after} records ({before - after} removed)")
    return df.reset_index(drop=True)


# ── Combined ─────────────────────────────────────────────────────────────────

def transform_all(raw: dict) -> dict:
    books = transform_books(raw["books"].copy())
    borrowers = transform_borrowers(raw["borrowers"].copy())
    transactions = transform_transactions(raw["transactions"].copy(), books, borrowers)
    total = len(books) + len(borrowers) + len(transactions)
    return {
        "books": books,
        "borrowers": borrowers,
        "transactions": transactions,
        "total_records": total,
    }
