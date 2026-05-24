from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Book(Base):
    __tablename__ = "books"

    book_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    author = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    isbn = Column(String, unique=True, nullable=False, index=True)
    availability_status = Column(String, default="available")  # available / borrowed

    transactions = relationship("Transaction", back_populates="book")

    def __repr__(self):
        return f"<Book(id={self.book_id}, title='{self.title}', status={self.availability_status})>"


class Borrower(Base):
    __tablename__ = "borrowers"

    borrower_id = Column(Integer, primary_key=True, index=True)
    borrower_name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)

    transactions = relationship("Transaction", back_populates="borrower")

    def __repr__(self):
        return f"<Borrower(id={self.borrower_id}, name='{self.borrower_name}', email={self.email})>"


class Transaction(Base):
    __tablename__ = "transactions"

    transaction_id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.book_id"), nullable=False)
    borrower_id = Column(Integer, ForeignKey("borrowers.borrower_id"), nullable=False)
    borrow_date = Column(DateTime, default=datetime.utcnow, index=True)
    due_date = Column(DateTime, nullable=True)
    return_date = Column(DateTime, nullable=True)

    book = relationship("Book", back_populates="transactions")
    borrower = relationship("Borrower", back_populates="transactions")

    def __repr__(self):
        return f"<Transaction(id={self.transaction_id}, book={self.book_id}, borrower={self.borrower_id})>"


# ── Phase 2: Analytics Tables ─────────────────────────────────────────────────

class MonthlyBorrowingTrend(Base):
    __tablename__ = "monthly_borrowing_trends"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    month_name = Column(String, nullable=True)
    total_borrowings = Column(Integer, default=0)
    total_returns = Column(Integer, default=0)
    active_loans = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class PopularBooksReport(Base):
    __tablename__ = "popular_books_report"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, nullable=False)
    title = Column(String, nullable=False)
    author = Column(String, nullable=False)
    category = Column(String, nullable=True)
    total_borrows = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


class CategoryBorrowingStats(Base):
    __tablename__ = "category_borrowing_stats"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    total_borrowings = Column(Integer, default=0)
    unique_borrowers = Column(Integer, default=0)
    avg_loan_days = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


class OverdueAnalytics(Base):
    __tablename__ = "overdue_analytics"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, nullable=False)
    book_id = Column(Integer, nullable=False)
    book_title = Column(String, nullable=True)
    borrower_id = Column(Integer, nullable=False)
    borrower_name = Column(String, nullable=True)
    borrow_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    days_overdue = Column(Integer, default=0)
    status = Column(String, default="overdue")
    created_at = Column(DateTime, default=datetime.utcnow)


class ETLRunLog(Base):
    __tablename__ = "etl_run_logs"

    id = Column(Integer, primary_key=True, index=True)
    run_at = Column(DateTime, default=datetime.utcnow)
    records_extracted = Column(Integer, default=0)
    records_transformed = Column(Integer, default=0)
    records_loaded = Column(Integer, default=0)
    status = Column(String, default="pending")  # pending / running / success / failed
    error_message = Column(String, nullable=True)
    duration_seconds = Column(Float, nullable=True)
