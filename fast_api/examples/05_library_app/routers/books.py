import sqlite3
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from schemas import BookIn, BookOut

router = APIRouter(prefix="/books", tags=["books"])

# available = total copies - loans not yet returned
BOOK_SELECT = """
SELECT b.*, b.total_copies - (
    SELECT COUNT(*) FROM loans l WHERE l.book_id = b.id AND l.returned_on IS NULL
) AS available_copies
FROM books b
"""


@router.get("", response_model=List[BookOut])
def list_books(author: Optional[str] = None, available: bool = False, db: sqlite3.Connection = Depends(get_db)):
    sql, args = BOOK_SELECT, []
    if author:
        sql += " WHERE b.author LIKE ?"
        args.append(f"%{author}%")
    rows = [dict(r) for r in db.execute(sql, args)]
    if available:
        rows = [r for r in rows if r["available_copies"] > 0]
    return rows


@router.get("/{book_id}", response_model=BookOut)
def get_book(book_id: int, db: sqlite3.Connection = Depends(get_db)):
    row = db.execute(BOOK_SELECT + " WHERE b.id = ?", (book_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Book not found")
    return dict(row)


@router.post("", response_model=BookOut, status_code=201)
def add_book(book: BookIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute(
            "INSERT INTO books (title, author, isbn, total_copies) VALUES (?, ?, ?, ?)",
            (book.title, book.author, book.isbn, book.total_copies),
        )
    except sqlite3.IntegrityError:
        raise HTTPException(409, f"ISBN {book.isbn} already exists")
    return {**book.model_dump(), "id": cur.lastrowid, "available_copies": book.total_copies}


@router.delete("/{book_id}", status_code=204)
def delete_book(book_id: int, db: sqlite3.Connection = Depends(get_db)):
    open_loans = db.execute(
        "SELECT COUNT(*) FROM loans WHERE book_id = ? AND returned_on IS NULL", (book_id,)
    ).fetchone()[0]
    if open_loans:
        raise HTTPException(409, "Cannot delete: book is currently borrowed")
    if db.execute("DELETE FROM books WHERE id = ?", (book_id,)).rowcount == 0:
        raise HTTPException(404, "Book not found")
