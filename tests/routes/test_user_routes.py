import pytest
from jose import jwt
from app import schemas
from app.config import settings

def test_root(client):
    res = client.get("/")
    assert res.json().get('message') == 'Welcome to Locallibrary-FastAPI'
    assert res.status_code == 200

def test_create_valid_user(client, test_roles):
    res = client.post(
        "/users/",
        json={
            "name": "anova patron",
            "email": "anova.patron@email.com",
            "password": "password01",
            "confirm_password": "password01"
        }
    )
    new_user = schemas.UserOut(**res.json())
    assert new_user.email == "anova.patron@email.com"
    assert new_user.role == "Patron"
    assert res.status_code == 201

def test_create_invalid_user_password(client, test_roles):
    res = client.post(
        "/users/",
        json={
            "name": "anova patron",
            "email": "anova.patron@email.com",
            "password": "password01",
            "confirm_password": "password02"
        }
    )
    assert res.status_code == 400
    assert res.status_code != 201

def test_create_invalid_user_email(client, test_roles):
    res = client.post(
        "/users/",
        json={
            "name": "anova patron",
            "email": "anova.patron.email.com",
            "password": "password01",
            "confirm_password": "password01"
        }
    )
    assert res.status_code == 422
    assert res.status_code != 201

def test_authorized_get_users(authorised_client, test_users):
    res = authorised_client.get("/users/")
    assert len(res.json()) == len(test_users)
    assert res.status_code == 200

def test_unauthorized_get_users(client, test_users):
    res = client.get("/users/")
    assert res.status_code == 401

def test_authorized_get_one_user(authorised_client, test_users):
    test_user = test_users[1]
    res = authorised_client.get(f"/users/{test_user['id']}")
    user = schemas.UserOut(**res.json())
    assert user.id == test_user['id']
    assert user.name == test_user['name']
    assert user.email == test_user['email']