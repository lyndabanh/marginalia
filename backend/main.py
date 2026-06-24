from fastapi import FastAPI
from database import Base, engine
import models
from routers import auth, users, books, userbooks, journal

app = FastAPI()
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(userbooks.router)
app.include_router(journal.router)

Base.metadata.create_all(engine)
