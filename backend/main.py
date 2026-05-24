"""
Library Management System - FastAPI Backend
Phase 2 Capstone Project
========================================

Extends Phase 1 with:
- ETL pipeline (Extract -> Transform -> Load) using Pandas CSV datasets
- Analytics tables: popular books, category stats, monthly trends, overdue analysis
- Analytics API endpoints
- ETL trigger and run-log endpoints
"""

from fastapi import FastAPI, Depends, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from typing import List

import models
import schemas
import crud
from database import engine, get_db
from routers import books, borrowers, transactions
from routers import analytics, etl_routes

# ──────────────────────────────────────────────────────────────────────────────
# Database Initialization
# ──────────────────────────────────────────────────────────────────────────────

# Create all database tables
models.Base.metadata.create_all(bind=engine)

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI Application Setup
# ──────────────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Library Management System API",
    description="A full-stack Library Management System with ETL analytics pipeline. Phase 2 Capstone Project.",
    version="2.0.0",
    contact={"name": "LMS Support"},
    license_info={"name": "MIT"},
)

# ──────────────────────────────────────────────────────────────────────────────
# CORS Configuration (allows React frontend)
# ──────────────────────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Include Routers
# ──────────────────────────────────────────────────────────────────────────────

app.include_router(books.router)
app.include_router(borrowers.router)
app.include_router(transactions.router)
app.include_router(analytics.router)
app.include_router(etl_routes.router)

# ──────────────────────────────────────────────────────────────────────────────
# Search Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get(
    "/search",
    response_model=List[schemas.BookResponse],
    tags=["Search"],
    summary="Search books across the catalog"
)
def search_books(
    q: str = Query(..., min_length=1, description="Search keyword (title, author, category, or ISBN)")
):
    """
    Search for books in the library catalog.
    
    Searches across:
    - Book titles
    - Author names
    - Categories
    - ISBN numbers
    
    Example: `/search?q=python`
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        return crud.search_books(db, q)
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# Dashboard Statistics Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/dashboard", tags=["Dashboard"], summary="Get library dashboard statistics")
def get_dashboard_statistics():
    """
    Get comprehensive library statistics and recent activity.
    
    Returns:
    - Total books in library
    - Available books count
    - Borrowed books count
    - Total registered borrowers
    - Total transactions
    - Active transactions (unreturned books)
    - Recent 5 transactions with details
    """
    from database import SessionLocal
    db = SessionLocal()
    try:
        total_books = db.query(models.Book).count()
        available_books = db.query(models.Book).filter(
            models.Book.availability_status == "available"
        ).count()
        borrowed_books = db.query(models.Book).filter(
            models.Book.availability_status == "borrowed"
        ).count()
        total_borrowers = db.query(models.Borrower).count()
        total_transactions = db.query(models.Transaction).count()
        active_transactions = db.query(models.Transaction).filter(
            models.Transaction.return_date == None
        ).count()

        # Fetch recent 5 transactions
        recent_transactions = db.query(models.Transaction).order_by(
            models.Transaction.borrow_date.desc()
        ).limit(5).all()

        recent = []
        for t in recent_transactions:
            recent.append({
                "transaction_id": t.transaction_id,
                "book_id": t.book_id,
                "book_title": t.book.title if t.book else "Unknown",
                "borrower_id": t.borrower_id,
                "borrower_name": t.borrower.borrower_name if t.borrower else "Unknown",
                "borrow_date": t.borrow_date.isoformat(),
                "return_date": t.return_date.isoformat() if t.return_date else None,
                "status": "returned" if t.return_date else "active"
            })

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "total_books": total_books,
            "available_books": available_books,
            "borrowed_books": borrowed_books,
            "total_borrowers": total_borrowers,
            "total_transactions": total_transactions,
            "active_transactions": active_transactions,
            "recent_transactions": recent
        }
    finally:
        db.close()


# ──────────────────────────────────────────────────────────────────────────────
# Health Check & Root Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/", tags=["Root"], summary="API health check")
def root():
    """
    Root endpoint - confirms API is running and provides navigation info.
    """
    return {
        "message": "Library Management System API v2.0 is running",
        "docs": "/docs",
        "redoc": "/redoc",
        "openapi": "/openapi.json",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat()
    }


# ──────────────────────────────────────────────────────────────────────────────
# Health Check Endpoint
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"], summary="Health status")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ──────────────────────────────────────────────────────────────────────────────
# Exception Handlers (can be extended)
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
