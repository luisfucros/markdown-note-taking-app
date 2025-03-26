from auth_lib import models
import pytest
from app import app
from auth_lib.oauth2 import create_access_token
from auth_lib.config import settings
from auth_lib.database import Base, get_db
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture()
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)


@pytest.fixture
def test_user2(client):
    user_data = {
        "name": "luis felipe",
        "email": "luis123@gmail.com",
        "password": "password123",
    }
    res = client.post("/users/register", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def test_user(client):
    user_data = {"name": "luis", "email": "luis@gmail.com", "password": "password123"}
    res = client.post("/users/register", json=user_data)

    assert res.status_code == 201

    new_user = res.json()
    new_user["email"] = user_data["email"]
    new_user["password"] = user_data["password"]
    return new_user


@pytest.fixture
def token(test_user):
    return create_access_token(
        {"user_id": test_user["id"], "user_email": test_user["email"]}
    )


@pytest.fixture
def authorized_client(client, token):
    client.headers = {**client.headers, "Authorization": f"Bearer {token}"}

    return client


@pytest.fixture
def test_notes(test_user, session, test_user2):
    notes_data = [
        {"title": "first title", "note": "first content", "owner_id": test_user["id"]},
        {"title": "2nd title", "note": "2nd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "note": "3rd content", "owner_id": test_user["id"]},
        {"title": "3rd title", "note": "3rd content", "owner_id": test_user2["id"]},
    ]

    def create_note_model(note):
        return models.Note(**note)

    note_map = map(create_note_model, notes_data)
    notes = list(note_map)

    session.add_all(notes)
    session.commit()

    notes = session.query(models.Note).all()
    return notes
