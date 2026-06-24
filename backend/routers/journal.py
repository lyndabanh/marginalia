from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, check_ownership
from models import UserBook, User, JournalEntry
from schemas import MessageResponse

router = APIRouter(prefix="/journal", tags=["journal"])

class AddJournalEntry(BaseModel):
    userbook_id: int
    content: str

class JournalEntrySummary(BaseModel):
    journalentry_id: int
    book_title: str
    created_at: datetime

class JournalEntryDetail(BaseModel):
    journalentry_id: int
    book_title: str
    content: str
    created_at: datetime

class UpdateJournalEntry(BaseModel):
    content: str

@router.post("/", response_model=JournalEntryDetail)
def add_entry(request: AddJournalEntry, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    userbook = db.scalars(select(UserBook).where(UserBook.id == request.userbook_id)).first()
    if not userbook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found on your shelf")

    check_ownership(userbook.user_id, current_user.id)

    journalentry = JournalEntry(
        user_id=userbook.user_id,
        book_id=userbook.book_id,
        content=request.content
    )

    db.add(journalentry)
    db.commit()
    db.refresh(journalentry)

    return JournalEntryDetail(
        journalentry_id=journalentry.id,
        book_title=journalentry.book.title,
        content=journalentry.content,
        created_at=journalentry.created_at
    )

@router.get("/", response_model=list[JournalEntrySummary])
def get_entries(book_id: int | None = None, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(JournalEntry).where(JournalEntry.user_id == current_user.id)
    if book_id:
        query = query.where(JournalEntry.book_id == book_id)
    entries = db.scalars(query).all()
    
    results = []
    for entry in entries:
        results.append(JournalEntrySummary(
            journalentry_id=entry.id,
            book_title=entry.book.title,
            created_at=entry.created_at
        ))
    
    return results

@router.get("/{entry_id}", response_model=JournalEntryDetail)
def get_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    journalentry = db.scalars(select(JournalEntry).where(JournalEntry.id == entry_id)).first()
    if not journalentry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    
    check_ownership(journalentry.user_id, current_user.id)

    return JournalEntryDetail(
        journalentry_id=journalentry.id,
        book_title=journalentry.book.title,
        content=journalentry.content,
        created_at=journalentry.created_at
    )

@router.put("/{entry_id}", response_model=JournalEntryDetail)
def update_entry(request: UpdateJournalEntry, entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    journalentry = db.scalars(select(JournalEntry).where(JournalEntry.id == entry_id)).first()
    if not journalentry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    check_ownership(journalentry.user_id, current_user.id)

    updates = request.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(journalentry, field, value)
    
    db.commit()
    db.refresh(journalentry)

    return JournalEntryDetail(
        journalentry_id=journalentry.id,
        book_title=journalentry.book.title,
        content=journalentry.content,
        created_at=journalentry.created_at
    )

@router.delete("/{entry_id}", response_model=MessageResponse)
def delete_entry(entry_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    journalentry = db.scalars(select(JournalEntry).where(JournalEntry.id == entry_id)).first()
    if not journalentry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal entry not found")
    check_ownership(journalentry.user_id, current_user.id)
    db.delete(journalentry)
    db.commit()

    return MessageResponse(message="Journal entry deleted")

@router.delete("/", response_model=MessageResponse)
def delete_entries_from_book(book_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    entries = db.scalars(select(JournalEntry).where(JournalEntry.user_id == current_user.id, JournalEntry.book_id == book_id)).all()
    if not entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No journal entries found")
    
    for entry in entries:
        db.delete(entry)
    db.commit()

    num_entries = len(entries)
    noun = "entry" if num_entries == 1 else "entries"
    return MessageResponse(message=f"{num_entries} journal {noun} deleted")
