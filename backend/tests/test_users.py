def test_get_me(client, auth_headers):
    response = client.get("/users/me", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["email"] == "test@test.com"

def test_get_user(client, auth_headers):
    me = client.get("/users/me", headers=auth_headers)
    user_id = me.json()["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test User"

def test_update_user(client, auth_headers):
    response = client.put("/users/me", json={"password": "updatedpassword"} , headers=auth_headers)
    assert response.status_code == 200
    
    login_response = client.post("/auth/login", json={
        "email": response.json()["email"],
        "password": "updatedpassword"
    })
    assert login_response.status_code == 200

def test_delete_me(client, auth_headers):
    response = client.delete("/users/me", headers=auth_headers)
    assert response.status_code == 200

    login_response = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert login_response.status_code == 401
