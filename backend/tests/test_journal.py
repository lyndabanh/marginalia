from tests.constants import THE_CORRESPONDENT, EAST_OF_EDEN

# test content for journal entries
CORRESPONDENT_ENTRIES = [
    "Sybil's voice feels so authentic. There is something quietly profound about a woman who has spent her life putting her thoughts into letters finally having to reckon with one she never sent.",
    "The pacing is slow but intentional. Each letter reveals another layer of who Sybil is, and I find myself reading more carefully than I usually do.",
    "I did not expect to feel so moved by the ending. The act of forgiveness here is not dramatic — it is quiet, almost offhand, which makes it hit harder."
]
EAST_OF_EDEN_ENTRY = "The Cain and Abel retelling feels inevitable in the best way — Steinbeck makes you forget you know how the story ends."

# test helper functions
def add_userbook(client, auth_headers, book):
    return client.post("/userbooks/", json=book, headers=auth_headers).json()

def add_entry(client, auth_headers, userbook_id, content):
    return client.post("/journal/", json={
        "userbook_id": userbook_id,
        "content": content
    }, headers=auth_headers).json()

# tests
def test_add_entry(client, auth_headers):
    nonexistant_userbook_response = client.post("/journal/", 
                                    json={"userbook_id": "99999", "content": EAST_OF_EDEN_ENTRY}, 
                                    headers=auth_headers)
    assert nonexistant_userbook_response.status_code == 404
    assert nonexistant_userbook_response.json()["detail"] == "Book not found on your shelf"

    add_userbook_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    userbook_id = add_userbook_response["userbook_id"]
    add_entry_response = add_entry(client, auth_headers, userbook_id, EAST_OF_EDEN_ENTRY)
    assert add_entry_response["book_title"] == "East of Eden"


def test_get_entries(client, auth_headers):
    add_correspondant_response = add_userbook(client, auth_headers, THE_CORRESPONDENT)
    correspondant_userbook_id = add_correspondant_response["userbook_id"]
    correspondant_book_id = add_correspondant_response["book_id"]
    for entry in CORRESPONDENT_ENTRIES:
        add_entry(client, auth_headers, correspondant_userbook_id, entry) 

    add_eden_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    eden_userbook_id = add_eden_response["userbook_id"]
    eden_book_id = add_eden_response["book_id"]
    add_entry(client, auth_headers, eden_userbook_id, EAST_OF_EDEN_ENTRY) 

    get_entries_response = client.get("/journal/", headers=auth_headers)
    assert len(get_entries_response.json()) == 4

    correspondant_entries_response = client.get("/journal/", params={"book_id": correspondant_book_id}, headers=auth_headers)
    assert len(correspondant_entries_response.json()) == 3

    eden_entries_response = client.get("/journal/", params={"book_id": eden_book_id}, headers=auth_headers)
    assert len(eden_entries_response.json()) == 1

def test_get_entry(client, auth_headers):
    get_nonexistant_entry_response = client.get(f"/journal/99999", headers=auth_headers)
    assert get_nonexistant_entry_response.status_code == 404

    add_userbook_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    userbook_id = add_userbook_response["userbook_id"]
    add_entry_response = add_entry(client, auth_headers, userbook_id, EAST_OF_EDEN_ENTRY)
    entry_id = add_entry_response["journalentry_id"]
    
    get_entry_response = client.get(f"/journal/{entry_id}", headers=auth_headers)
    assert get_entry_response.json()["book_title"] == "East of Eden"

def test_update_entry(client, auth_headers):
    add_userbook_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    userbook_id = add_userbook_response["userbook_id"]
    add_entry_response = add_entry(client, auth_headers, userbook_id, EAST_OF_EDEN_ENTRY)
    entry_id = add_entry_response["journalentry_id"]

    new_content = "Returning to this after finishing — the inevitability I felt early on holds. What surprised me is how much sympathy Steinbeck asks you to carry for characters who do not deserve it."
    update_entry_response = client.put(f"/journal/{entry_id}", json={"content": new_content}, headers=auth_headers)
    assert update_entry_response.status_code == 200
    assert "Returning to this after finishing" in update_entry_response.json()["content"]

def test_delete_entry(client, auth_headers):
    add_userbook_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    userbook_id = add_userbook_response["userbook_id"]
    add_entry_response = add_entry(client, auth_headers, userbook_id, EAST_OF_EDEN_ENTRY)
    entry_id = add_entry_response["journalentry_id"]

    delete_entry_response = client.delete(f"/journal/{entry_id}", headers=auth_headers)
    assert delete_entry_response.status_code == 200

    get_entry_response = client.get(f"/journal/{entry_id}", headers=auth_headers)
    assert get_entry_response.status_code == 404

def test_delete_entries_from_book(client, auth_headers):
    add_correspondant_response = add_userbook(client, auth_headers, THE_CORRESPONDENT)
    correspondant_userbook_id = add_correspondant_response["userbook_id"]
    correspondant_book_id = add_correspondant_response["book_id"]
    for entry in CORRESPONDENT_ENTRIES:
        add_entry(client, auth_headers, correspondant_userbook_id, entry) 

    add_eden_response = add_userbook(client, auth_headers, EAST_OF_EDEN)
    eden_userbook_id = add_eden_response["userbook_id"]
    add_entry(client, auth_headers, eden_userbook_id, EAST_OF_EDEN_ENTRY)

    client.delete("/journal/", params={"book_id": correspondant_book_id}, headers=auth_headers)
    get_entries_response = client.get("/journal/", headers=auth_headers)
    assert len(get_entries_response.json()) == 1
    assert get_entries_response.json()[0]["book_title"] == "East of Eden"
