import os
import pytest
import random
from app.config import settings
from app.main import app
from dotenv import load_dotenv
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.database import Model, get_db
from app.models import *
from app.utils import hash
from app.oauth2 import create_access_token
from faker import Faker
from fastapi.testclient import TestClient

# load_dotenv()

DATABASE_URL = f"postgresql+psycopg2://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}"+"_test"

engine = sa.create_engine(DATABASE_URL)
TestSession = so.sessionmaker(engine)

fake = Faker()
Faker.seed(0)
unique_isbns = set()

def generate_unique_isbn():
    while True:
        isbn = fake.isbn13()
        if isbn not in unique_isbns:
            unique_isbns.add(isbn)
            return isbn

@pytest.fixture()
def session():
    print('Session fixture ran')
    Model.metadata.drop_all(bind=engine)
    Model.metadata.create_all(bind=engine)
    db = TestSession()
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

@pytest.fixture()
def test_author(session):
    author = Author(name='Samanosuke Akechi')
    session.add(author)
    session.commit()
    return author

@pytest.fixture()
def test_book(test_author, session):
    book = Book(
        title = fake.sentence(nb_words=5),
        summary = fake.sentence(nb_words=50),
        isbn = generate_unique_isbn(),
        author = test_author
    )
    session.add(book)

    for i in range(random.randint(1, 5)):
        bk = BookInstance(
            imprint=fake.company(),
            status=random.choice(list(StatusEnum))
        )
        book.book_instances.append(bk)
    
    session.commit()
    return book

@pytest.fixture()
def test_roles(session):
    Role.insert_roles(session)
    roles = session.scalars(sa.select(Role).order_by(Role.name.asc())).all()
    roles_dict = {}
    for role in roles:
        roles_dict[role.name] = role
    return roles_dict

@pytest.fixture()
def test_user(session, test_roles):
    user = User( 
        name="main admin",
        email="main.admin@email.com",
        password=hash("password01"),
        role=test_roles["Admin"]
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user.to_dict()

@pytest.fixture()
def token(test_user):
    return create_access_token({"user_id": test_user["id"]})

@pytest.fixture()
def authorised_client(client, token):
    client.headers = {
        **client.headers,
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture()
def test_users(session, test_roles):
    users_data = [
        {
            "name": "first patron",
            "email": "first.patron@email.com",
            "password": "password01",
            "role" : test_roles["Patron"]
        },
        {
            "name": "second patron",
            "email": "second.patron@email.com",
            "password": "password01",
            "role" : test_roles["Patron"]
        },
        {
            "name": "da librarian",
            "email": "da.librarian@email.com",
            "password": "password01",
            "role" : test_roles["Librarian"]
        },
        {
            "name": "da Admin",
            "email": "da.admin@email.com",
            "password": "password01",
            "role" : test_roles["Admin"]
        }
    ]
    def create_users(user):
        return User(**user)
    
    user_map = map(create_users, users_data)
    users = list(user_map)

    session.add_all(users)
    session.commit()
    users = session.execute(sa.select(User)).all()
    # return users
    return [{**user[0].to_dict()} for user in users]

    