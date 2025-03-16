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
    res = authorized_client.get(f"/notes/88888")
    assert res.status_code == 404


def test_get_one_note(authorized_client, test_notes):
    res = authorized_client.get(f"/notes/{test_notes[0].id}")
    note = note_schemas.NoteOut(**res.json())
    assert note.id == test_notes[0].id
    assert note.note == test_notes[0].note
    assert note.title == test_notes[0].title