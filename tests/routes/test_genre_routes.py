import pytest
from app import schemas

def test_authorised_create_genre(authorised_client):
    res = authorised_client.post(
        "/genres/",
        json={
            "name" : "Igbo Fantasy"
        }
    )
    genre = schemas.GenreOut(**res.json())
    assert genre.name == 'Igbo Fantasy'
    assert res.status_code == 201

def test_unauthorised_create_genre(client):
    res = client.post(
        "/genres/",
        json={
            "name" : "Igbo Fantasy"
        }
    )
    assert res.status_code == 401

def test_update_genre(test_genre, authorised_client):
    res = authorised_client.put(
        f"/genres/{test_genre.id}",
        json={
            "name" : "Igbo Folktale"
        }
    )
    genre = schemas.GenreOut(**res.json())
    print(genre)
    assert genre.name == test_genre.name
    assert genre.name == "Igbo Folktale"

def test_delete_genre(test_genre, authorised_client):
    res = authorised_client.delete(
        f"/genres/{test_genre.id}"
    )
    assert res.status_code == 204