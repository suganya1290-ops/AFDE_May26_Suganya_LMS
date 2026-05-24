"""
ETL Phase – Load
Insert cleaned DataFrames into the SQLite database and rebuild analytics tables.
"""

import pandas as pd
from datetime import datetime, date
from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import models


# ── Core entity loaders ───────────────────────────────────────────────────────

def load_books(session: Session, books_df: pd.DataFrame) -> dict:
    """Upsert books; return {csv_book_id -> db_book_id}."""
    id_map = {}
    for _, row in books_df.iterrows():
        isbn = str(row["isbn"]).strip()
        existing = session.query(models.Book).filter(models.Book.isbn == isbn).first()
        if existing:
            id_map[int(row["book_id"])] = existing.book_id
        else:
            book = models.Book(
                title=str(row["title"]).strip(),
                author=str(row["author"]).strip(),
                category=str(row["category"]).strip(),
                isbn=isbn,
            )
            session.add(book)
            session.flush()
            id_map[int(row["book_id"])] = book.book_id
    session.commit()
    print(f"[Load] Books loaded: {len(id_map)}")
    return id_map


def load_borrowers(session: Session, borrowers_df: pd.DataFrame) -> dict:
    """Upsert borrowers; return {csv_borrower_id -> db_borrower_id}."""
    id_map = {}
    for _, row in borrowers_df.iterrows():
        email = str(row["email"]).strip().lower()
        existing = session.query(models.Borrower).filter(models.Borrower.email == email).first()
        if existing:
            id_map[int(row["borrower_id"])] = existing.borrower_id
        else:
            borrower = models.Borrower(
                borrower_name=str(row["borrower_name"]).strip(),
                email=email,
                phone=str(row.get("phone", "N/A")).strip(),
            )
            session.add(borrower)
            session.flush()
            id_map[int(row["borrower_id"])] = borrower.borrower_id
    session.commit()
    print(f"[Load] Borrowers loaded: {len(id_map)}")
    return id_map


def load_transactions(session: Session, transactions_df: pd.DataFrame, book_id_map: dict, borrower_id_map: dict) -> int:
    """Insert transactions using mapped DB IDs; skip existing (same book+borrower+borrow_date)."""
    loaded = 0
    for _, row in transactions_df.iterrows():
        csv_book_id = int(row["book_id"])
        csv_borrower_id = int(row["borrower_id"])
        db_book_id = book_id_map.get(csv_book_id)
        db_borrower_id = borrower_id_map.get(csv_borrower_id)
        if db_book_id is None or db_borrower_id is None:
            continue

        borrow_date = row["borrow_date"]
        if pd.isna(borrow_date):
            continue
        borrow_date = borrow_date.to_pydatetime()

        existing = session.query(models.Transaction).filter(
            models.Transaction.book_id == db_book_id,
            models.Transaction.borrower_id == db_borrower_id,
            models.Transaction.borrow_date == borrow_date,
        ).first()
        if existing:
            continue

        due_date = row.get("due_date")
        return_date = row.get("return_date")
        due_dt = due_date.to_pydatetime() if pd.notna(due_date) else None
        ret_dt = return_date.to_pydatetime() if pd.notna(return_date) else None

        txn = models.Transaction(
            book_id=db_book_id,
            borrower_id=db_borrower_id,
            borrow_date=borrow_date,
            due_date=due_dt,
            return_date=ret_dt,
        )
        session.add(txn)
        loaded += 1

    session.commit()
    print(f"[Load] Transactions loaded: {loaded}")
    return loaded


# ── Analytics table builders ──────────────────────────────────────────────────

def build_popular_books(session: Session):
    """Truncate and rebuild popular_books_report from transactions."""
    session.query(models.PopularBooksReport).delete()

    rows = (
        session.query(
            models.Transaction.book_id,
            models.Book.title,
            models.Book.author,
            models.Book.category,
        )
        .join(models.Book, models.Transaction.book_id == models.Book.book_id)
        .all()
    )

    from collections import Counter
    counts = Counter((r.book_id, r.title, r.author, r.category) for r in rows)

    for (book_id, title, author, category), total in counts.most_common():
        session.add(models.PopularBooksReport(
            book_id=book_id,
            title=title,
            author=author,
            category=category or "General",
            total_borrows=total,
        ))
    session.commit()
    print(f"[Load] Popular books report: {len(counts)} entries")


def build_category_stats(session: Session):
    """Truncate and rebuild category_borrowing_stats."""
    session.query(models.CategoryBorrowingStats).delete()

    rows = (
        session.query(models.Transaction, models.Book)
        .join(models.Book, models.Transaction.book_id == models.Book.book_id)
        .all()
    )

    from collections import defaultdict
    stats: dict = defaultdict(lambda: {"count": 0, "borrowers": set(), "loan_days": []})

    for txn, book in rows:
        cat = book.category or "General"
        stats[cat]["count"] += 1
        stats[cat]["borrowers"].add(txn.borrower_id)
        if txn.return_date and txn.borrow_date:
            days = (txn.return_date - txn.borrow_date).days
            stats[cat]["loan_days"].append(days)

    for cat, s in stats.items():
        avg_days = round(sum(s["loan_days"]) / len(s["loan_days"]), 2) if s["loan_days"] else 0.0
        session.add(models.CategoryBorrowingStats(
            category=cat,
            total_borrowings=s["count"],
            unique_borrowers=len(s["borrowers"]),
            avg_loan_days=avg_days,
        ))
    session.commit()
    print(f"[Load] Category stats: {len(stats)} categories")


def build_monthly_trends(session: Session):
    """Truncate and rebuild monthly_borrowing_trends."""
    session.query(models.MonthlyBorrowingTrend).delete()

    txns = session.query(models.Transaction).all()

    from collections import defaultdict
    MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                   "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    data: dict = defaultdict(lambda: {"borrows": 0, "returns": 0})

    for t in txns:
        if t.borrow_date:
            key = (t.borrow_date.year, t.borrow_date.month)
            data[key]["borrows"] += 1
        if t.return_date:
            key = (t.return_date.year, t.return_date.month)
            data[key]["returns"] += 1

    for (year, month), vals in sorted(data.items()):
        active = vals["borrows"] - vals["returns"]
        session.add(models.MonthlyBorrowingTrend(
            year=year,
            month=month,
            month_name=MONTH_NAMES[month],
            total_borrowings=vals["borrows"],
            total_returns=vals["returns"],
            active_loans=max(active, 0),
        ))
    session.commit()
    print(f"[Load] Monthly trends: {len(data)} month buckets")


def build_overdue_analytics(session: Session):
    """Truncate and rebuild overdue_analytics for unreturned past-due transactions."""
    session.query(models.OverdueAnalytics).delete()

    today = datetime.utcnow()
    txns = (
        session.query(models.Transaction)
        .filter(
            models.Transaction.return_date == None,
            models.Transaction.due_date != None,
            models.Transaction.due_date < today,
        )
        .all()
    )

    for t in txns:
        days_overdue = (today - t.due_date).days
        book_title = t.book.title if t.book else "Unknown"
        borrower_name = t.borrower.borrower_name if t.borrower else "Unknown"
        session.add(models.OverdueAnalytics(
            transaction_id=t.transaction_id,
            book_id=t.book_id,
            book_title=book_title,
            borrower_id=t.borrower_id,
            borrower_name=borrower_name,
            borrow_date=t.borrow_date,
            due_date=t.due_date,
            days_overdue=days_overdue,
            status="overdue",
        ))
    session.commit()
    print(f"[Load] Overdue analytics: {len(txns)} overdue transactions")


# ── Book availability sync ────────────────────────────────────────────────────

def sync_book_availability(session: Session):
    """Set availability_status on every book based on unreturned transactions."""
    session.query(models.Book).update({"availability_status": "available"},
                                      synchronize_session="fetch")

    active_ids = [
        row.book_id for row in
        session.query(models.Transaction.book_id)
        .filter(models.Transaction.return_date == None)
        .distinct()
        .all()
    ]

    if active_ids:
        session.query(models.Book).filter(
            models.Book.book_id.in_(active_ids)
        ).update({"availability_status": "borrowed"}, synchronize_session="fetch")

    session.commit()
    print(f"[Load] Book availability synced: {len(active_ids)} marked borrowed")


# ── Master load function ──────────────────────────────────────────────────────

def load_all(session: Session, clean: dict) -> int:
    book_id_map = load_books(session, clean["books"])
    borrower_id_map = load_borrowers(session, clean["borrowers"])
    txn_count = load_transactions(session, clean["transactions"], book_id_map, borrower_id_map)

    sync_book_availability(session)
    build_popular_books(session)
    build_category_stats(session)
    build_monthly_trends(session)
    build_overdue_analytics(session)

    total_loaded = len(book_id_map) + len(borrower_id_map) + txn_count
    return total_loaded
