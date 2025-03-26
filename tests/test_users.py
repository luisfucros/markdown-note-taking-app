import jwt
import pytest
from auth_lib.config import settings
from auth_lib.schemas import token_schemas


def test_create_user(client):
    res = client.post(
        "/users/register",
        json={
            "name": "hello",
            "email": "hello123@gmail.com",
            "password": "password123",
        },
    )

    token = token_schemas.Token(**res.json())
    assert isinstance(token.access_token, str)
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    login_res = token_schemas.Token(**res.json())
    payload = jwt.decode(
        login_res.access_token, settings.secret_key, algorithms=[settings.algorithm]
    )
    email = payload.get("user_email")
    assert email == test_user["email"]
    assert login_res.token_type == "bearer"
    assert res.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", "password123", 403),
        ("luiss@gmail.com", "wrongpassword", 403),
        ("wrongemail@gmail.com", "wrongpassword", 403),
        (None, "password123", 403),
        ("luiss@gmail.com", None, 403),
    ],
)
def test_incorrect_login(test_user, client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code
    assert res.json().get("detail") == "Invalid Credentials"
