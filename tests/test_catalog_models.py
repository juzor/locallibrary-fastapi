import pytest
import sqlalchemy as sa
import sqlalchemy.orm as so
from app.models import *

def test_get_authors(test_author):
    assert test_author.name == 'Samanosuke Akechi'

def test_author_books(test_book, test_author):
    assert test_book is not None
    assert test_book.author == test_author
    assert test_book.author.name == test_author.name

def test_book_instance(session, test_book, test_author):
    book_instances = session.scalars(sa.select(BookInstance).where(BookInstance.book_id == test_book.id)).all()
    assert len(book_instances) > 0
    for instance in book_instances:
        assert instance.book == test_book
        assert instance.book.author == test_author

def test_book_genre(session, test_genre, test_book):
    # scalar returns the first value of the first row or None if the query has no result
    book = session.scalar(sa.select(Book).where(Book.title == test_book.title)) 
    book.genres.append(test_genre)
    session.commit()

    genre = session.scalar(sa.select(Genre).where(Genre.name == test_genre.name))
    assert book.genres[0].name == genre.name
    assert book.genres[0].id == genre.id

def test_book_lang(session, test_book):
    lang = Language(name="English")
    lang.books.add(test_book)
    session.add(lang)
    session.commit()

    assert lang.name == test_book.language.name




# TODO - refactor all test to read from database