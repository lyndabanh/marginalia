from fastapi import FastAPI
from database import Base, engine
import models
from routers import auth

app = FastAPI()
app.include_router(auth.router)

Base.metadata.create_all(engine)
