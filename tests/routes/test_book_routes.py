import pytest
from app import schemas

def test_create_valid_book(authorised_client, test_author, test_language):
    res = authorised_client.post(
        "/books/",
        json={
            "title": "Alogbaga",
            "summary": "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
            "isbn": "597-0-07-698456-5",
            "img_url": "placeholder image",
            "language_id": test_language.id,
            "author_id": test_author.id,
            "copies": 2,
            "imprint": "Nwosu print",
            "genres": [
                "Igbo Folktale",
                "Fantasy"
            ]
        }
    )
    new_book = schemas.BookOut(**res.json())
    assert res.status_code == 201
    assert new_book.title == "Alogbaga"


def test_create_invalid_book(authorised_client):
        res = authorised_client.post(
            "/books/",
            json={
                "title": "Testing new book",
                "summary": "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
                "isbn": "597-0-07-698456-5",
                "img_url": "placeholder image",
                "language_id": None,
                "author_id": None,
                "copies": 2,
                "imprint": "leicester print"
            }
        )
        # bad_book = schemas.BookOut(**res.json())
        assert res.status_code == 404

def test_get_book(authorised_client, test_book):
    res = authorised_client.get(
         f"/books/{test_book.id}"
    )
    book = schemas.BookDetailOut(**res.json())
    print(book)
    assert res.status_code == 200
    assert book.title == test_book.title

def test_update_book(authorised_client, test_book):
    res = authorised_client.put(
         f"/books/{test_book.id}",
         json = {
            "title": f"{test_book.title} updated",
            "summary": "new book summary",
            "isbn" : test_book.isbn,
            "img_url": "placeholder img"
        }
    )
    updated_book = schemas.BookOut(**res.json())
    print(updated_book)
    assert res.status_code == 200
    assert updated_book.title == test_book.title
    assert updated_book.author == test_book.author.name

def test_delete_book(authorised_client, test_book):
    res = authorised_client.delete(
        f"/books/{test_book.id}"
    )

    assert res.status_code == 204