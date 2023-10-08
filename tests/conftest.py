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
    return roles

    