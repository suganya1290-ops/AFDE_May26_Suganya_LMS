from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── Book Schemas ──────────────────────────────────────────────────────────────

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Book title")
    author: str = Field(..., min_length=1, max_length=255, description="Author name")
    category: str = Field(..., min_length=1, max_length=100, description="Book category")
    isbn: str = Field(..., min_length=10, max_length=20, description="ISBN number")
    availability_status: Optional[str] = Field(default="available", description="Available or Borrowed")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    isbn: Optional[str] = Field(None, min_length=10, max_length=20)
    availability_status: Optional[str] = None


class BookResponse(BookBase):
    book_id: int

    class Config:
        from_attributes = True


# ── Borrower Schemas ──────────────────────────────────────────────────────────

class BorrowerBase(BaseModel):
    borrower_name: str = Field(..., min_length=1, max_length=255, description="Borrower full name")
    email: str = Field(..., description="Email address")
    phone: str = Field(..., description="Phone number")


class BorrowerCreate(BorrowerBase):
    phone: str = Field(..., min_length=5, max_length=20, description="Phone number")


class BorrowerUpdate(BaseModel):
    borrower_name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[str] = None
    phone: Optional[str] = Field(None, min_length=5, max_length=20)


class BorrowerResponse(BorrowerBase):
    borrower_id: int

    class Config:
        from_attributes = True


# ── Transaction Schemas ───────────────────────────────────────────────────────

class BorrowRequest(BaseModel):
    book_id: int = Field(..., description="Book ID to borrow")
    borrower_id: int = Field(..., description="Borrower ID")


class ReturnRequest(BaseModel):
    book_id: int = Field(..., description="Book ID to return")
    borrower_id: int = Field(..., description="Borrower ID")


class TransactionResponse(BaseModel):
    transaction_id: int
    book_id: int
    borrower_id: int
    borrow_date: datetime
    return_date: Optional[datetime] = None
    book: Optional[BookResponse] = None
    borrower: Optional[BorrowerResponse] = None

    class Config:
        from_attributes = True
