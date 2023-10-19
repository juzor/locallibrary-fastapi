import pytest
from app import schemas

def test_authorised_create_lang(authorised_client):
    res = authorised_client.post(
        "/languages/",
        json={
            "name" : "Igbo"
        }
    )
    language = schemas.LangOut(**res.json())
    assert language.name == 'Igbo'
    assert res.status_code == 201

def test_unauthorised_create_lang(client):
    res = client.post(
        "/languages/",
        json={
            "name" : "Igbo"
        }
    )
    assert res.status_code == 401

def test_update_language(test_lang, authorised_client):
    res = authorised_client.put(
        f"/languages/{test_lang.id}",
        json={
            "name" : "Igbo"
        }
    )
    lang = schemas.LangOut(**res.json())
    print(lang)
    assert lang.name == test_lang.name
    assert lang.name == "Igbo"

def test_delete_lang(test_lang, authorised_client):
    res = authorised_client.delete(
        f"/languages/{test_lang.id}"
    )
    assert res.status_code == 204