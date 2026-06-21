from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user
from models import ReadingStatus, UserBook, User, Book
from schemas import MessageResponse

router = APIRouter(prefix="/userbooks", tags=["userbooks"])

class AddUserBook(BaseModel):
    isbn: str
    title: str
    author: str
    cover_image: str | None = None
    genre: str | None = None
    summary: str | None = None
    status: ReadingStatus = ReadingStatus.want_to_read

class UserBookSummary(BaseModel):
    userbook_id: int
    title: str
    author: str
    cover_image: str | None = None
    genre: str | None = None
    status: ReadingStatus

class UserBookDetail(BaseModel):
    userbook_id: int
    title: str
    author: str
    cover_image: str | None = None
    genre: str | None = None
    summary: str | None = None
    rating: int | None = None
    review: str | None = None
    date_started: datetime | None = None
    date_finished: datetime | None = None
    status: ReadingStatus

class UpdateUserBook(BaseModel):
    status: ReadingStatus | None = None
    rating: int | None = None 
    review: str | None = None
    date_started: datetime | None = None
    date_finished: datetime | None = None

@router.post("/", response_model=MessageResponse)
def add_to_shelf(request: AddUserBook, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    book = db.scalars(select(Book).where(Book.isbn == request.isbn)).first()
    if not book:
        book = Book(
            isbn=request.isbn,
            title=request.title,
            author=request.author,
            cover_image=request.cover_image,
            genre=request.genre,
            summary=request.summary
        )
        db.add(book)
        db.commit()
        db.refresh(book)

    existing = db.scalars(select(UserBook).where(UserBook.user_id == current_user.id, UserBook.book_id == book.id)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Book already on your shelf")
    
    userbook = UserBook(
        user_id=current_user.id,
        book_id=book.id,
        status=request.status
    )
    db.add(userbook)
    db.commit()
    
    return MessageResponse(message=f"{book.title} by {book.author} has been added to your bookshelf")

@router.get("/user/{user_id}", response_model=list[UserBookSummary])
def get_bookshelf(user_id: int, db: Session = Depends(get_db)):
    if not db.scalars(select(User).where(User.id == user_id)).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    userbooks = db.scalars(select(UserBook).where(UserBook.user_id == user_id)).all()
    
    result = []
    for userbook in userbooks:
        result.append(UserBookSummary(
            userbook_id=userbook.id,
            title=userbook.book.title,
            author=userbook.book.author,
            cover_image=userbook.book.cover_image,
            genre=userbook.book.genre,
            status=userbook.status
        ))

    return result

@router.get("/{userbook_id}", response_model=UserBookDetail)
def get_userbook(userbook_id: int, db: Session = Depends(get_db)):
    userbook = db.scalars(select(UserBook).where(UserBook.id == userbook_id)).first()
    if not userbook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Userbook not found")
    
    return UserBookDetail(
        userbook_id=userbook.id,
        title=userbook.book.title,
        author=userbook.book.author,
        cover_image=userbook.book.cover_image,
        genre=userbook.book.genre,
        summary=userbook.book.summary,
        rating=userbook.rating,
        review=userbook.review,
        date_started=userbook.date_started,
        date_finished=userbook.date_finished,
        status=userbook.status
    )
