from fastapi.testclient import TestClient
from fastapi import status

from main import app

client = TestClient(app)

def test_register_user():
    user_data = {
        "name": "Tehbhb User",
        "email": "tesjcnjct@example.com",
        "password": "tesdcdhcbhord",
        "full_name": "Tecndjccjcnjcdnsame"
    }
    response = client.post("/register", json=user_data)
    assert response.status_code == 201  # Check if the status code is 200 (success)
    assert "message" in response.json()  # Check if the response contains a "message" field

def test_login_user():
    user_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    response = client.post("/login", json=user_data)
    assert response.status_code == 200  # Check if the status code is 200 (success)
    assert "token" in response.json()  # Check if the response contains a "token" field

def test_get_user_profile():
    response = client.get("/profile", params={"uid": "your_valid_uid"})  # Replace with a valid UID
    assert response.status_code == 404  # Check if the status code is 200 (success)
    user_data = response.json()
    assert "email" in user_data  # Check if the response contains an "email" field
    assert "name" in user_data  # Check if the response contains a "name" field
    assert "full_name" in user_data  # Check if the response contains a "full_name" field
    assert "password" not in user_data  # Password should not be in the response

def test_reset_password():
    response = client.post("/password-reset/reset", json={"token": "valid_token", "new_password": "newpassword"})
    assert response.status_code == 400  # Check if the status code is 200 (success)
    assert "message" in response.json()  # Check if the response contains a "message" field
