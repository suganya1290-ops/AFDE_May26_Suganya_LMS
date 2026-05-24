"""
Analytics API Routes – Phase 2
Serves pre-computed data from ETL analytics tables.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

import models
from database import get_db

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/popular-books", summary="Top N most borrowed books")
def get_popular_books(
    limit: int = Query(10, ge=1, le=50, description="Number of top books to return"),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(models.PopularBooksReport)
        .order_by(models.PopularBooksReport.total_borrows.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "rank": i + 1,
            "book_id": r.book_id,
            "title": r.title,
            "author": r.author,
            "category": r.category,
            "total_borrows": r.total_borrows,
        }
        for i, r in enumerate(rows)
    ]


@router.get("/category-stats", summary="Borrowing statistics grouped by book category")
def get_category_stats(db: Session = Depends(get_db)):
    rows = (
        db.query(models.CategoryBorrowingStats)
        .order_by(models.CategoryBorrowingStats.total_borrowings.desc())
        .all()
    )
    return [
        {
            "category": r.category,
            "total_borrowings": r.total_borrowings,
            "unique_borrowers": r.unique_borrowers,
            "avg_loan_days": r.avg_loan_days,
        }
        for r in rows
    ]


@router.get("/monthly-trends", summary="Monthly borrowing and return counts")
def get_monthly_trends(
    year: int = Query(None, description="Filter by year (e.g. 2024). Returns all years if omitted."),
    db: Session = Depends(get_db),
):
    query = db.query(models.MonthlyBorrowingTrend).order_by(
        models.MonthlyBorrowingTrend.year,
        models.MonthlyBorrowingTrend.month,
    )
    if year:
        query = query.filter(models.MonthlyBorrowingTrend.year == year)
    rows = query.all()
    return [
        {
            "year": r.year,
            "month": r.month,
            "month_name": r.month_name,
            "label": f"{r.month_name} {r.year}",
            "total_borrowings": r.total_borrowings,
            "total_returns": r.total_returns,
            "active_loans": r.active_loans,
        }
        for r in rows
    ]


@router.get("/overdue", summary="List all overdue transactions")
def get_overdue_transactions(db: Session = Depends(get_db)):
    rows = (
        db.query(models.OverdueAnalytics)
        .order_by(models.OverdueAnalytics.days_overdue.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "transaction_id": r.transaction_id,
            "book_id": r.book_id,
            "book_title": r.book_title,
            "borrower_id": r.borrower_id,
            "borrower_name": r.borrower_name,
            "borrow_date": r.borrow_date.isoformat() if r.borrow_date else None,
            "due_date": r.due_date.isoformat() if r.due_date else None,
            "days_overdue": r.days_overdue,
            "status": r.status,
        }
        for r in rows
    ]


@router.get("/summary", summary="High-level analytics summary card")
def get_analytics_summary(db: Session = Depends(get_db)):
    total_analyzed = db.query(models.Transaction).count()
    overdue_count = db.query(models.OverdueAnalytics).count()
    categories = db.query(models.CategoryBorrowingStats).count()
    top_book = (
        db.query(models.PopularBooksReport)
        .order_by(models.PopularBooksReport.total_borrows.desc())
        .first()
    )
    top_category = (
        db.query(models.CategoryBorrowingStats)
        .order_by(models.CategoryBorrowingStats.total_borrowings.desc())
        .first()
    )
    return {
        "total_transactions_analyzed": total_analyzed,
        "overdue_count": overdue_count,
        "categories_tracked": categories,
        "top_book": top_book.title if top_book else None,
        "top_book_borrows": top_book.total_borrows if top_book else 0,
        "top_category": top_category.category if top_category else None,
        "top_category_borrowings": top_category.total_borrowings if top_category else 0,
    }
