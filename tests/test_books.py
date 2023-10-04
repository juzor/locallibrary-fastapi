import pytest
from faker import Faker
from app.models import Author, Book

fake = Faker()
Faker.seed(0)
unique_isbns = set()

def generate_unique_isbn():
    while True:
        isbn = fake.isbn13()
        if isbn not in unique_isbns:
            unique_isbns.add(isbn)
            return isbn

def test_author(session):
    book = Book(
        title='Test 1', 
        summary='book summary',#
        isbn = generate_unique_isbn()
    )

    author = Author(name='Foo Bar')
    session.add(author)

    author.books.append(book)

    session.commit()

    assert author.name == 'Foo Bar'
    assert author.id is not None
    assert len(author.books) > 0