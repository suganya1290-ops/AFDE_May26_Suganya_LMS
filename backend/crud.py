from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import datetime
import models
import schemas
from fastapi import HTTPException, status


# ──────────────────────────────────────────────────────────────────────────────
# BOOK OPERATIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_books(db: Session, skip: int = 0, limit: int = 100):
    """Get all books with pagination"""
    return db.query(models.Book).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int):
    """Get book by ID"""
    book = db.query(models.Book).filter(models.Book.book_id == book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Book with ID {book_id} not found"
        )
    return book


def create_book(db: Session, book: schemas.BookCreate):
    """Create a new book"""
    existing = db.query(models.Book).filter(models.Book.isbn == book.isbn).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ISBN already exists in the system"
        )
    
    db_book = models.Book(**book.model_dump())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def update_book(db: Session, book_id: int, book: schemas.BookUpdate):
    """Update book details"""
    db_book = get_book(db, book_id)
    update_data = book.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_book, key, value)
    
    db.commit()
    db.refresh(db_book)
    return db_book


def delete_book(db: Session, book_id: int):
    """Delete a book"""
    db_book = get_book(db, book_id)
    db.delete(db_book)
    db.commit()
    return {"message": f"Book {book_id} deleted successfully"}


def search_books(db: Session, query: str):
    """Search books by title, author, category, or ISBN"""
    return db.query(models.Book).filter(
        or_(
            models.Book.title.ilike(f"%{query}%"),
            models.Book.author.ilike(f"%{query}%"),
            models.Book.category.ilike(f"%{query}%"),
            models.Book.isbn.ilike(f"%{query}%"),
        )
    ).all()


# ──────────────────────────────────────────────────────────────────────────────
# BORROWER OPERATIONS
# ──────────────────────────────────────────────────────────────────────────────

def get_borrowers(db: Session, skip: int = 0, limit: int = 100):
    """Get all borrowers with pagination"""
    return db.query(models.Borrower).offset(skip).limit(limit).all()


def get_borrower(db: Session, borrower_id: int):
    """Get borrower by ID"""
    borrower = db.query(models.Borrower).filter(models.Borrower.borrower_id == borrower_id).first()
    if not borrower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Borrower with ID {borrower_id} not found"
        )
    return borrower


def create_borrower(db: Session, borrower: schemas.BorrowerCreate):
    """Create a new borrower"""
    existing_email = db.query(models.Borrower).filter(models.Borrower.email == borrower.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in the system"
        )
    
    db_borrower = models.Borrower(**borrower.model_dump())
    db.add(db_borrower)
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def update_borrower(db: Session, borrower_id: int, borrower: schemas.BorrowerUpdate):
    """Update borrower details"""
    db_borrower = get_borrower(db, borrower_id)
    update_data = borrower.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(db_borrower, key, value)
    
    db.commit()
    db.refresh(db_borrower)
    return db_borrower


def delete_borrower(db: Session, borrower_id: int):
    """Delete a borrower"""
    db_borrower = get_borrower(db, borrower_id)
    db.delete(db_borrower)
    db.commit()
    return {"message": f"Borrower {borrower_id} deleted successfully"}


# ──────────────────────────────────────────────────────────────────────────────
# TRANSACTION OPERATIONS
# ──────────────────────────────────────────────────────────────────────────────

def borrow_book(db: Session, request: schemas.BorrowRequest):
    """Record a book borrow transaction"""
    # Verify book exists and is available
    book = get_book(db, request.book_id)
    if book.availability_status != "available":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Book is not available for borrowing"
        )
    
    # Verify borrower exists
    get_borrower(db, request.borrower_id)
    
    # Create transaction
    transaction = models.Transaction(
        book_id=request.book_id,
        borrower_id=request.borrower_id,
        borrow_date=datetime.utcnow()
    )
    
    # Update book status
    book.availability_status = "borrowed"
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def return_book(db: Session, request: schemas.ReturnRequest):
    """Record a book return transaction"""
    # Find active transaction (not yet returned)
    transaction = db.query(models.Transaction).filter(
        models.Transaction.book_id == request.book_id,
        models.Transaction.borrower_id == request.borrower_id,
        models.Transaction.return_date == None
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No active borrowing transaction found for this book and borrower"
        )
    
    # Update transaction
    transaction.return_date = datetime.utcnow()
    
    # Update book status
    book = get_book(db, request.book_id)
    book.availability_status = "available"
    
    db.commit()
    db.refresh(transaction)
    return transaction


def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    """Get all transactions with pagination"""
    return db.query(models.Transaction).offset(skip).limit(limit).all()


def get_active_transactions(db: Session):
    """Get only active (non-returned) transactions"""
    return db.query(models.Transaction).filter(models.Transaction.return_date == None).all()
