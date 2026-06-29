def test_register(client):
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login(registered_user, client):
    response = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_register_duplicate_email(registered_user, client):
    response = client.post("/auth/register", json={
        "name": "Test User",
        "email": "test@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 400

def test_login_wrong_password(registered_user, client):
    response = client.post("/auth/login", json={
        "email": "test@test.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_login_nonexistent_email(client):
    response = client.post("/auth/login", json={
        "email": "wrongemail@test.com",
        "password": "testpassword"
    })
    assert response.status_code == 401
        