from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/books",
    tags=["Books Management"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[schemas.BookResponse], summary="Get all books")
def get_all_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all books in the library with pagination support.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    """
    return crud.get_books(db, skip=skip, limit=limit)


@router.get("/{book_id}", response_model=schemas.BookResponse, summary="Get book by ID")
def get_book_by_id(book_id: int, db: Session = Depends(get_db)):
    """Get a specific book by its ID"""
    return crud.get_book(db, book_id)


@router.post("/", response_model=schemas.BookResponse, status_code=status.HTTP_201_CREATED, summary="Add new book")
def create_new_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    """
    Create a new book entry in the library.
    
    - **title**: Book title (required)
    - **author**: Author name (required)
    - **category**: Book category (required)
    - **isbn**: ISBN number, must be unique (required)
    - **availability_status**: Available or Borrowed (default: available)
    """
    return crud.create_book(db, book)


@router.put("/{book_id}", response_model=schemas.BookResponse, summary="Update book")
def update_book_details(
    book_id: int,
    book: schemas.BookUpdate,
    db: Session = Depends(get_db)
):
    """Update book information"""
    return crud.update_book(db, book_id, book)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete book")
def delete_book_by_id(book_id: int, db: Session = Depends(get_db)):
    """Delete a book from the library"""
    crud.delete_book(db, book_id)
    return None
