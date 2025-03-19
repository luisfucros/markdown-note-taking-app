import pytest
from schemas import note_schemas


def test_get_all_notes(authorized_client, test_notes):
    res = authorized_client.get("/notes")

    def validate(note):
        return note_schemas.NoteResponse(**note)

    notes_map = validate(res.json())
    notes_list = notes_map.data

    assert len(res.json()["data"]) == len(notes_list)
    assert res.status_code == 200


def test_unauthorized_user_get_all_notes(client, test_notes):
    res = client.get("/notes")
    assert res.status_code == 401


def test_unauthorized_user_get_one_note(client, test_notes):
    res = client.get(f"/notes/{test_notes[0].id}")
    assert res.status_code == 401


def test_get_one_note_not_exist(authorized_client, test_notes):
    res = authorized_client.get("/notes/88888")
    assert res.status_code == 404


def test_get_one_note(authorized_client, test_notes):
    res = authorized_client.get(f"/notes/{test_notes[0].id}")
    note = note_schemas.NoteOut(**res.json())
    assert note.id == test_notes[0].id
    assert note.note == test_notes[0].note
    assert note.title == test_notes[0].title


@pytest.mark.parametrize(
    "title, note",
    [
        ("awesome new title", "awesome new note"),
        ("favorite pizza", "i love pepperoni"),
        ("remember", "remember note"),
    ],
)
def test_create_note(authorized_client, test_user, test_notes, title, note):
    res = authorized_client.post("/notes", json={"title": title, "note": note})

    created_note = note_schemas.NoteOut(**res.json())
    assert res.status_code == 201
    assert created_note.title == title
    assert created_note.note == note
    assert created_note.owner_id == test_user["id"]


def test_unauthorized_user_create_note(client, test_user, test_notes):
    res = client.post("/notes", json={"title": "some title", "note": "something"})
    assert res.status_code == 401


def test_unauthorized_user_delete_note(client, test_user, test_notes):
    res = client.delete(f"/notes/{test_notes[0].id}")
    assert res.status_code == 401


def test_delete_note_success(authorized_client, test_user, test_notes):
    res = authorized_client.delete(f"/notes/{test_notes[0].id}")

    assert res.status_code == 204


def test_delete_note_non_exist(authorized_client, test_user, test_notes):
    res = authorized_client.delete("/notes/8000000")

    assert res.status_code == 404


def test_delete_other_user_note(authorized_client, test_user, test_notes):
    res = authorized_client.delete(f"/notes/{test_notes[3].id}")
    assert res.status_code == 403


def test_update_note(authorized_client, test_user, test_notes):
    data = {"title": "updated title", "note": "updated note", "id": test_notes[0].id}
    res = authorized_client.put(f"/notes/{test_notes[0].id}", json=data)
    updated_note = note_schemas.NoteOut(**res.json())
    assert res.status_code == 200
    assert updated_note.title == data["title"]
    assert updated_note.note == data["note"]


def test_update_other_user_notes(authorized_client, test_user, test_user2, test_notes):
    data = {"title": "updated title", "note": "updated note", "id": test_notes[3].id}
    res = authorized_client.put(f"/notes/{test_notes[3].id}", json=data)
    assert res.status_code == 403


def test_unauthorized_user_update_notes(client, test_user, test_notes):
    res = client.put(f"/notes/{test_notes[0].id}")
    assert res.status_code == 401


def test_update_note_non_exist(authorized_client, test_user, test_notes):
    data = {"title": "updated title", "note": "updated note", "id": test_notes[3].id}
    res = authorized_client.put("/notes/8000000", json=data)

    assert res.status_code == 404
