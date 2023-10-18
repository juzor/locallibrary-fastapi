import pytest
from app import schemas

def test_create_valid_author(authorised_client):
    res = authorised_client.post(
        "/authors/",
        json={
            "name" : "Foo Bar"
        }
    )
    author = schemas.AuthorOut(**res.json())
    assert author.name == "Foo Bar"
    assert res.status_code == 201

def test_create_invalid_author(authorised_client):
    res = authorised_client.post(
        "/authors/",
        json={
            "name" : "",
            "date_of_birth": "",
            "date_of_death": ""
        }
    )
    assert res.status_code == 422

def test_update_author(test_author, authorised_client):
    res = authorised_client.put(
        f"/authors/{test_author.id}",
        json={
            "name":"Samanosuke Akechi - updated",
            "date_of_birth": "1957-06-12T00:00:00.000000"
        }
    )
    author = schemas.AuthorOut(**res.json())
    assert author.name == test_author.name
    assert author.name == "Samanosuke Akechi - updated"
    assert author.date_of_birth == test_author.date_of_birth
    assert author.date_of_death == test_author.date_of_death

def test_delete_author(test_author, authorised_client):
    res = authorised_client.delete(
        f"/authors/{test_author.id}"
    )

    assert res.status_code == 204