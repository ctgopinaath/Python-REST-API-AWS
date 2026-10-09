import sqlite3
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from database import get_db
from schemas import MemberIn, MemberOut

router = APIRouter(prefix="/members", tags=["members"])


@router.get("", response_model=List[MemberOut])
def list_members(db: sqlite3.Connection = Depends(get_db)):
    return [dict(r) for r in db.execute("SELECT * FROM members")]


@router.post("", response_model=MemberOut, status_code=201)
def add_member(member: MemberIn, db: sqlite3.Connection = Depends(get_db)):
    try:
        cur = db.execute("INSERT INTO members (name, email) VALUES (?, ?)", (member.name, member.email))
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Email already registered")
    return {**member.model_dump(), "id": cur.lastrowid}
