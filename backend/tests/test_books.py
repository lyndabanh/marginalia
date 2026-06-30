from unittest.mock import patch, MagicMock

def test_book_search(client):
    fake_google_books_response = {
        "items": [
            {
                "kind": "books#volume",
                "id": "tYqPMQEACAAJ",
                "etag": "D9MZ6ZiMjHg",
                "selfLink": "https://www.googleapis.com/books/v1/volumes/tYqPMQEACAAJ",
                "volumeInfo": {
                    "title": "Catch 22",
                    "authors": [
                        "Joseph Heller"
                        ],
                    "publisher": "Grasset & Fasquelle",
                    "publishedDate": "2000",
                    "description": "Catch 22, l'Article 22, est un \"attrape-nigaud\" qui permet à un colonel américain d'imposer un nombre de missions sans cesse croissant à son escadrille de bombardement basée dans une petite île de la Méditerranée pendant la Seconde Guerre mondiale. Yossarian, héros tragi-comique de cette épopée burlesque, est décidé à tout tenter pour sauver sa peau : il estime que sa seule mission, quand il s'envole, consiste à atterrir vivant. Simuler la folie dans cet univers délirant lui paraît le meilleur moyen de tirer au flanc. Hélas, l'Article 22 stipule : \" Quiconque veut se faire dispenser d'aller au feu n'est pas réellement fou. \" Cette première œuvre de Joseph Heller compte parmi les meilleurs romans américains de l'après-guerre.",
                    "industryIdentifiers": [
                        {
                        "type": "ISBN_10",
                        "identifier": "2246269318"
                        },
                        {
                        "type": "ISBN_13",
                        "identifier": "9782246269311"
                        }
                    ],
                    "pageCount": 510,
                    "printType": "BOOK",
                    "categories": [
                        "War stories"
                    ],
                    "language": "fr",
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.json.return_value = fake_google_books_response

    with patch("routers.books.httpx.get", return_value=mock_response):
        response = client.get("/books/search?q=catch22")

    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Catch 22"
    assert results[0]["author"] == "Joseph Heller"
    assert results[0]["isbn"] == "9782246269311"
    assert results[0]["genre"] == "War stories"

def test_book_search_missing_author(client):
        fake_google_books_response = {
            "items": [
                {
                    "kind": "books#volume",
                    "id": "pCrcEAAAQBAJ",
                    "volumeInfo": {
                        "title": "Untitled Red Tower 2023 Release",
                        "publisher": "Entangled: Red Tower Books",
                        "publishedDate": "2023-11-07",
                        "description": "New Red Tower Release Coming Soon!",
                        "industryIdentifiers": [
                            {"type": "ISBN_13", "identifier": "9781649376169"},
                            {"type": "ISBN_10", "identifier": "1649376162"}
                        ],
                        "categories": ["Fiction"],
                        "language": "en"
                    }
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = fake_google_books_response

        with patch("routers.books.httpx.get", return_value=mock_response):
             response = client.get("books/search?q=fourthwing")
        
        assert response.status_code == 200
        results = response.json()
        assert len(results) == 1
        assert results[0]["title"] == "Untitled Red Tower 2023 Release"
        assert results[0]["author"] is None
        assert results[0]["isbn"] == "9781649376169"

def test_book_search_isbn10_conversion(client):
    fake_google_books_response = {
        "items": [
            {
                "kind": "books#volume",
                "id": "BzDHAAAACAAJ",
                "volumeInfo": {
                    "title": "Rebecca.",
                    "subtitle": "Simplified edition.",
                    "authors": ["Daphne DuMaurier"],
                    "publishedDate": "1996-01",
                    "industryIdentifiers": [
                        {"type": "ISBN_10", "identifier": "3526275068"}
                    ],
                    "pageCount": 106,
                    "language": "en"
                }
            }
        ]
    }

    mock_response = MagicMock()
    mock_response.json.return_value = fake_google_books_response

    with patch("routers.books.httpx.get", return_value=mock_response):
         response = client.get("/books/search?q=rebecca")
        
    assert response.status_code == 200
    results = response.json()
    assert results[0]["isbn"] == "9783526275060"
    