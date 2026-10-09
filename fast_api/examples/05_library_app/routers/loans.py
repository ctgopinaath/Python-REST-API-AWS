"""
Business rules (the "complex" part):
  1. A book can only be borrowed if a copy is available.
  2. A member can hold at most MAX_LOANS books at a time.
  3. A member with an overdue book cannot borrow anything new.
  4. Returning late costs FINE_PER_DAY rupees per day.
"""
import sqlite3
from datetime import date, timedelta
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from database import get_db
from schemas import BorrowIn, LoanOut

router = APIRouter(prefix="/loans", tags=["loans"])

MAX_LOANS = 3
FINE_PER_DAY = 5


def calc_fine(due_on: date, returned_on: Optional[date]) -> int:
    end = returned_on or date.today()
    late_days = (end - due_on).days
    return max(0, late_days) * FINE_PER_DAY


def to_loan(row: sqlite3.Row) -> dict:
    d = dict(row)
    due = date.fromisoformat(d["due_on"])
    ret = date.fromisoformat(d["returned_on"]) if d["returned_on"] else None
    d["fine"] = calc_fine(due, ret)
    return d


def send_receipt(member_id: int, message: str) -> None:
    # Runs AFTER the response is sent. Replace with real email/SMS.
    print(f"[receipt] member={member_id}: {message}")


@router.post("/borrow", response_model=LoanOut, status_code=201)
def borrow(req: BorrowIn, background: BackgroundTasks, db: sqlite3.Connection = Depends(get_db)):
    book = db.execute("SELECT * FROM books WHERE id = ?", (req.book_id,)).fetchone()
    if not book:
        raise HTTPException(404, "Book not found")
    if not db.execute("SELECT 1 FROM members WHERE id = ?", (req.member_id,)).fetchone():
        raise HTTPException(404, "Member not found")

    borrowed = db.execute(
        "SELECT COUNT(*) FROM loans WHERE book_id = ? AND returned_on IS NULL", (req.book_id,)
    ).fetchone()[0]
    if borrowed >= book["total_copies"]:
        raise HTTPException(409, "No copies available")

    active = db.execute(
        "SELECT due_on FROM loans WHERE member_id = ? AND returned_on IS NULL", (req.member_id,)
    ).fetchall()
    if len(active) >= MAX_LOANS:
        raise HTTPException(409, f"Loan limit reached ({MAX_LOANS} books)")
    if any(date.fromisoformat(r["due_on"]) < date.today() for r in active):
        raise HTTPException(403, "Member has overdue books - return them first")

    today = date.today()
    due = today + timedelta(days=req.days)
    cur = db.execute(
        "INSERT INTO loans (book_id, member_id, borrowed_on, due_on) VALUES (?, ?, ?, ?)",
        (req.book_id, req.member_id, today.isoformat(), due.isoformat()),
    )
    background.add_task(send_receipt, req.member_id, f"Borrowed '{book['title']}', due {due}")
    return to_loan(db.execute("SELECT * FROM loans WHERE id = ?", (cur.lastrowid,)).fetchone())


@router.post("/{loan_id}/return", response_model=LoanOut)
def return_book(loan_id: int, background: BackgroundTasks, db: sqlite3.Connection = Depends(get_db)):
    loan = db.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone()
    if not loan:
        raise HTTPException(404, "Loan not found")
    if loan["returned_on"]:
        raise HTTPException(409, "Already returned")
    db.execute("UPDATE loans SET returned_on = ? WHERE id = ?", (date.today().isoformat(), loan_id))
    result = to_loan(db.execute("SELECT * FROM loans WHERE id = ?", (loan_id,)).fetchone())
    background.add_task(send_receipt, result["member_id"], f"Returned loan {loan_id}, fine Rs.{result['fine']}")
    return result


@router.get("", response_model=List[LoanOut])
def list_loans(member_id: Optional[int] = None, active_only: bool = False, db: sqlite3.Connection = Depends(get_db)):
    sql, args = "SELECT * FROM loans WHERE 1=1", []
    if member_id is not None:
        sql += " AND member_id = ?"
        args.append(member_id)
    if active_only:
        sql += " AND returned_on IS NULL"
    return [to_loan(r) for r in db.execute(sql, args)]


@router.get("/overdue", response_model=List[LoanOut])
def overdue(db: sqlite3.Connection = Depends(get_db)):
    rows = db.execute(
        "SELECT * FROM loans WHERE returned_on IS NULL AND due_on < ?", (date.today().isoformat(),)
    )
    return [to_loan(r) for r in rows]
