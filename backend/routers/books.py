import os
from dotenv import load_dotenv
from fastapi import APIRouter
import httpx
from pydantic import BaseModel
from utils import isbn10_to_isbn13

load_dotenv()

GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY")
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes?q="

router = APIRouter(prefix="/books", tags=["books"])

class BookSearchResult(BaseModel):
    title: str
    author: str | None = None
    isbn: str | None = None
    cover_image: str | None = None
    genre: str | None = None
    summary: str | None = None
    
@router.get("/search", response_model=list[BookSearchResult])
def search(q: str):
    full_url = f"{GOOGLE_BOOKS_API_URL}{q}&key={GOOGLE_BOOKS_API_KEY}"
    response = httpx.get(full_url)
    data = response.json()

    results = []
    for item in data["items"]:
        isbn = None
        for identifier in item["volumeInfo"].get("industryIdentifiers", []):
            if identifier["type"] == "ISBN_13":
                isbn = identifier["identifier"]
                break
            elif identifier["type"] == "ISBN_10":
                isbn = isbn10_to_isbn13(str(identifier["identifier"]))

        categories = item["volumeInfo"].get("categories", [])
        genre = ", ".join(categories) if categories else None

        results.append(BookSearchResult(
            title=item["volumeInfo"]["title"],
            author=item["volumeInfo"]["authors"][0] if item["volumeInfo"].get("authors") else None,
            isbn=isbn,
            cover_image=item["volumeInfo"].get("imageLinks", {}).get("thumbnail"),
            genre=genre,
            summary=item["volumeInfo"].get("description")
        ))
    
    return results
