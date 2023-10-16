import pytest
from jose import jwt
from app import schemas
from app.config import settings

def test_login_route(client, test_user):
    res = client.post(
        "/login",
        data={
            "username": test_user['email'],
            "password": 'password01'
        }
    )
    
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token,
        settings.secret_key, 
        algorithms=[settings.algorithm]
    )
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200