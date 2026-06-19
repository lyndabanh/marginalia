from datetime import datetime, timezone
import enum
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint, ForeignKey, Enum

from database import Base

class ReadingStatus(enum.Enum):
    reading = "reading"
    finished = "finished"
    abandoned = "abandoned"
    want_to_read = "want_to_read"

class QuestionSource(enum.Enum):
    ai_notes = "ai_notes"
    ai_general = "ai_general"
    user = "user"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True, index=True)
    location: Mapped[Optional[str]]
    avatar: Mapped[Optional[str]]
    password_hash: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))

class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(unique=True)
    title: Mapped[str]
    author: Mapped[str]
    cover_image: Mapped[Optional[str]]
    genre: Mapped[Optional[str]]
    summary: Mapped[Optional[str]]
    deleted_at: Mapped[Optional[datetime]]

class UserBook(Base):
    __tablename__ = "userbooks"
    __table_args__ = (UniqueConstraint("user_id", "book_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"), index=True)
    status: Mapped[ReadingStatus] = mapped_column(Enum(ReadingStatus), default=ReadingStatus.want_to_read)
    rating: Mapped[Optional[int]]
    review: Mapped[Optional[str]]
    date_started: Mapped[Optional[datetime]]
    date_finished: Mapped[Optional[datetime]]
    book: Mapped["Book"] = relationship("Book")
    user: Mapped["User"] = relationship("User")

class JournalEntry(Base):
    __tablename__ = "journalentries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    content: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    book: Mapped["Book"] = relationship("Book")
    user: Mapped["User"] = relationship("User")

class DiscussionQuestion(Base):
    __tablename__ = "discussionquestions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))
    question_text: Mapped[str]
    chapter: Mapped[Optional[int]]
    source: Mapped[QuestionSource] = mapped_column(Enum(QuestionSource))
    is_shared: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    book: Mapped["Book"] = relationship("Book")
    user: Mapped["User"] = relationship("User")