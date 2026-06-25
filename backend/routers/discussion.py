from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from dependencies import get_current_user, check_ownership
from models import UserBook, User, DiscussionQuestion, QuestionSource
from schemas import MessageResponse

router = APIRouter(prefix="/discussion", tags=["discussion"])

class AddDiscussionQuestion(BaseModel):
    userbook_id: int
    question_text: str
    chapter: int | None = None
    is_shared: bool = False

class DiscussionQuestionSummary(BaseModel):
    discussionquestion_id: int
    user_name: str
    book_title: str
    question_text: str
    is_shared: bool
    created_at: datetime

class DiscussionQuestionDetail(BaseModel):
    discussionquestion_id: int
    user_name: str
    book_title: str
    question_text: str
    chapter: int | None = None
    source: QuestionSource
    is_shared: bool
    created_at: datetime

class UpdateDiscussionQuestion(BaseModel):
    question_text: str | None = None
    chapter: int | None = None
    is_shared: bool | None = None

@router.post("/", response_model=DiscussionQuestionDetail)
def add_question(request: AddDiscussionQuestion, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    userbook = db.scalars(select(UserBook).where(UserBook.id == request.userbook_id)).first()
    if not userbook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found on your shelf")
    check_ownership(userbook.user_id, current_user.id)

    question = DiscussionQuestion(
        user_id=userbook.user_id,
        book_id=userbook.book_id,
        question_text=request.question_text,
        chapter=request.chapter,
        source=QuestionSource.user,
        is_shared=request.is_shared
    )

    db.add(question)
    db.commit()
    db.refresh(question)

    return DiscussionQuestionDetail(
        discussionquestion_id=question.id,
        user_name=current_user.name,
        book_title=userbook.book.title,
        question_text=question.question_text,
        chapter=question.chapter,
        source=question.source,
        is_shared=question.is_shared,
        created_at=question.created_at
    )

@router.get("/", response_model=list[DiscussionQuestionSummary])
def get_questions(user_id: int | None = None, 
                  book_id: int | None = None, 
                  current_user: User = Depends(get_current_user), 
                  db: Session = Depends(get_db)):
    
    query = select(DiscussionQuestion)
    if user_id and user_id != current_user.id:
        query = query.where(DiscussionQuestion.user_id == user_id, DiscussionQuestion.is_shared == True)
    else:
        query = query.where(DiscussionQuestion.user_id == current_user.id)
    
    if book_id:
        query = query.where(DiscussionQuestion.book_id == book_id)
    questions = db.scalars(query).all()

    results = []
    for question in questions:
        results.append(DiscussionQuestionSummary(
            discussionquestion_id=question.id,
            user_name=question.user.name,
            book_title=question.book.title,
            question_text=question.question_text,
            is_shared=question.is_shared,
            created_at=question.created_at
        ))
    return results

@router.get("/{question_id}", response_model=DiscussionQuestionDetail)
def get_question(question_id: int,
                 current_user: User = Depends(get_current_user),
                 db: Session = Depends(get_db)):
    question = db.scalars(select(DiscussionQuestion).where(DiscussionQuestion.id == question_id)).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    if question.user_id != current_user.id and not question.is_shared:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This question is private")
    
    return DiscussionQuestionDetail(
        discussionquestion_id=question.id,
        user_name=question.user.name,
        book_title=question.book.title,
        question_text=question.question_text,
        chapter=question.chapter,
        source=question.source,
        is_shared=question.is_shared,
        created_at=question.created_at
    )
        
@router.put("/{question_id}", response_model=DiscussionQuestionDetail)
def update_question(request: UpdateDiscussionQuestion,
                    question_id: int,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    question = db.scalars(select(DiscussionQuestion).where(DiscussionQuestion.id == question_id)).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    check_ownership(question.user_id, current_user.id)

    updates = request.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(question, field, value)
    
    db.commit()
    db.refresh(question)

    return DiscussionQuestionDetail(
        discussionquestion_id=question.id,
        user_name=question.user.name,
        book_title=question.book.title,
        question_text=question.question_text,
        chapter=question.chapter,
        source=question.source,
        is_shared=question.is_shared,
        created_at=question.created_at
    )

@router.delete("/{question_id}", response_model=MessageResponse)
def delete_question(question_id: int,
                    current_user: User = Depends(get_current_user),
                    db: Session = Depends(get_db)):
    question = db.scalars(select(DiscussionQuestion).where(DiscussionQuestion.id == question_id)).first()
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    
    check_ownership(question.user_id, current_user.id)

    db.delete(question)
    db.commit()

    return MessageResponse(message="Discussion question deleted")
