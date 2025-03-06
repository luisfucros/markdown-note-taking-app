from typing import Optional

import markdown
import models
from fastapi import Depends
from repositories.note import NoteRepository
from schemas import note_schemas, user_schemas


class NoteService:
    """
    Service class for handling note-related operations.
    """

    def __init__(self, note_repository: NoteRepository = Depends()):
        self.note_repo = note_repository

    def get_note(
        self, note_id: int, user: user_schemas.UserOut
    ) -> Optional[models.Note]:
        """
        Retrieve a specific note by its ID for a given user.

        Args:
            note_id (int): The ID of the note to retrieve.
            user (user_schemas.UserOut): The user requesting the note.

        Returns:
            str: The note content converted to HTML.
        """
        note = self.note_repo.get_note(note_id, user)
        return note

    def get_markdown_note(
        self, note_id: int, user: user_schemas.UserOut
    ) -> Optional[str]:
        note = self.get_note(note_id, user)
        if note is None:
            return None

        try:
            content = note.note
            html = markdown.markdown(content)
            return html
        except Exception as e:
            # todo
            print(e)
            raise

    def get_notes(
        self,
        user: user_schemas.UserOut,
        limit: int,
        page: int,
        search: Optional[str] = "",
    ) -> note_schemas.NoteResponse:
        """
        Retrieve a paginated list of notes for a user.

        Args:
            user (user_schemas.UserOut): The user requesting the notes.
            limit (int): The number of notes to return per page.
            page (int): The page number to retrieve.
            search (Optional[str]): Optional search term to filter notes.

        Returns:
            note_schemas.NoteResponse: A response object containing the paginated notes.
        """
        notes, total = self.note_repo.get_notes(user, limit, page, search)

        response = note_schemas.NoteResponse(
            data=notes, limit=limit, page=page, total=total
        )
        return response

    def create_note(
        self, note: note_schemas.NoteCreate, user: user_schemas.UserOut
    ) -> models.Note:
        """
        Create a new note.

        Args:
            note (note_schemas.NoteCreate): The note data to create.
            user (user_schemas.UserOut): The user creating the note.

        Returns:
            models.Note: The created note.
        """
        return self.note_repo.create_note(note, user)

    def update_note(
        self,
        note_id: int,
        updated_note_info: note_schemas.NoteCreate,
        user: user_schemas.UserOut,
    ) -> models.Note:
        """
        Update an existing note.

        Args:
            note_id (int): The ID of the note to update.
            updated_note_info (note_schemas.NoteCreate): The updated note data.
            user (user_schemas.UserOut): The user requesting the update.

        Returns:
            models.Note: The updated note.
        """
        note = self.note_repo.update_note(note_id, updated_note_info, user)
        return note

    def delete_note(self, note_id: int, user: user_schemas.UserOut) -> bool:
        """
        Delete a note.

        Args:
            note_id (int): The ID of the note to delete.
            user (user_schemas.UserOut): The user requesting deletion.

        Returns:
            Optional[Response]: A response indicating successful deletion.
        """
        response = self.note_repo.delete_note(note_id, user)
        return response
