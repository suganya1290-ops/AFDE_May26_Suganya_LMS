from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.orm import Session
from typing import List
import crud
import schemas
from database import get_db

router = APIRouter(
    prefix="/borrowers",
    tags=["Borrowers Management"],
    responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=List[schemas.BorrowerResponse], summary="Get all borrowers")
def get_all_borrowers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    Get all borrowers registered in the library system.
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100, max: 1000)
    """
    return crud.get_borrowers(db, skip=skip, limit=limit)


@router.get("/{borrower_id}", response_model=schemas.BorrowerResponse, summary="Get borrower by ID")
def get_borrower_by_id(borrower_id: int, db: Session = Depends(get_db)):
    """Get a specific borrower by their ID"""
    return crud.get_borrower(db, borrower_id)


@router.post("/", response_model=schemas.BorrowerResponse, status_code=status.HTTP_201_CREATED, summary="Add new borrower")
def create_new_borrower(borrower: schemas.BorrowerCreate, db: Session = Depends(get_db)):
    """
    Register a new borrower in the library system.
    
    - **borrower_name**: Full name of the borrower (required)
    - **email**: Email address, must be unique (required)
    - **phone**: Contact phone number (required)
    """
    return crud.create_borrower(db, borrower)


@router.put("/{borrower_id}", response_model=schemas.BorrowerResponse, summary="Update borrower")
def update_borrower_details(
    borrower_id: int,
    borrower: schemas.BorrowerUpdate,
    db: Session = Depends(get_db)
):
    """Update borrower information"""
    return crud.update_borrower(db, borrower_id, borrower)


@router.delete("/{borrower_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete borrower")
def delete_borrower_by_id(borrower_id: int, db: Session = Depends(get_db)):
    """Delete a borrower record from the system"""
    crud.delete_borrower(db, borrower_id)
    return None
