from tests.constants import EAST_OF_EDEN

def test_add_to_shelf(client, auth_headers):
    response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "East of Eden"

def test_add_same_book_to_shelf(client, auth_headers):
    response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    assert response.status_code == 200

    add_same_book_response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    assert add_same_book_response.status_code == 400

def test_get_bookshelf(client, auth_headers):
    client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)

    me = client.get("/users/me", headers=auth_headers)
    user_id = me.json()["id"]
    response = client.get(f"/userbooks/user/{user_id}")
    assert response.status_code == 200 
    assert response.json()[0]["title"] == "East of Eden"

def test_get_userbook(client, auth_headers):
    add_response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    userbook_id = add_response.json()["userbook_id"]

    response = client.get(f"/userbooks/{userbook_id}")
    userbook = response.json()
    assert userbook["title"] == "East of Eden"
    assert userbook["summary"] == "A masterpiece of Biblical scope, and the magnum opus of one of America's most enduring authors, in a commemorative hardcover edition."

def test_update_userbook(client, auth_headers):
    add_response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    userbook_id = add_response.json()["userbook_id"]

    get_response = client.get(f"/userbooks/{userbook_id}")
    userbook = get_response.json()
    assert userbook["title"] == "East of Eden"
    assert userbook["status"] == "want_to_read"

    update_response = client.put(f"/userbooks/{userbook_id}", json={"status": "reading"}, headers=auth_headers)
    updated_userbook = update_response.json()
    assert updated_userbook["status"] == "reading"

def test_delete_userbook(client, auth_headers):
    add_response = client.post("/userbooks/", json=EAST_OF_EDEN, headers=auth_headers)
    userbook_id = add_response.json()["userbook_id"]

    get_response = client.get(f"/userbooks/{userbook_id}")
    userbook = get_response.json()
    assert userbook["title"] == "East of Eden"

    delete_response = client.delete(f"/userbooks/{userbook_id}", headers=auth_headers)
    assert delete_response.status_code == 200

    get_deleted_response = client.get(f"/userbooks/{userbook_id}")
    assert get_deleted_response.status_code == 404
