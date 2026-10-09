from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class BookIn(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1)
    isbn: str = Field(pattern=r"^\d{10}(\d{3})?$")  # ISBN-10 or ISBN-13 digits
    total_copies: int = Field(1, ge=1, le=50)


class BookOut(BookIn):
    id: int
    available_copies: int


class MemberIn(BaseModel):
    name: str = Field(min_length=2)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class MemberOut(MemberIn):
    id: int


class BorrowIn(BaseModel):
    book_id: int
    member_id: int
    days: int = Field(14, ge=1, le=30)


class LoanOut(BaseModel):
    id: int
    book_id: int
    member_id: int
    borrowed_on: date
    due_on: date
    returned_on: Optional[date] = None
    fine: int = 0  # in rupees
