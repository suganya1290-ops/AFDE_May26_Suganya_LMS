from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db

router = APIRouter(
    tags=["Transactions Management"],
    responses={404: {"description": "Not found"}}
)


@router.post("/borrow", response_model=schemas.TransactionResponse, status_code=status.HTTP_201_CREATED, summary="Borrow a book")
def borrow_book_transaction(
    request: schemas.BorrowRequest,
    db: Session = Depends(get_db)
):
    """
    Record a book borrow transaction.
    
    Updates:
    - Creates a transaction record with current timestamp
    - Changes book availability status to "borrowed"
    
    Validations:
    - Book must exist and be available
    - Borrower must exist in the system
    """
    return crud.borrow_book(db, request)


@router.post("/return", response_model=schemas.TransactionResponse, summary="Return a book")
def return_book_transaction(
    request: schemas.ReturnRequest,
    db: Session = Depends(get_db)
):
    """
    Record a book return transaction.
    
    Updates:
    - Sets return_date on the active transaction
    - Changes book availability status back to "available"
    
    Validations:
    - An active (unreturned) borrowing transaction must exist
    """
    return crud.return_book(db, request)


@router.get("/transactions", response_model=List[schemas.TransactionResponse], summary="Get all transactions")
def get_all_transactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all borrow/return transactions in the library system.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    """
    return crud.get_transactions(db, skip=skip, limit=limit)
