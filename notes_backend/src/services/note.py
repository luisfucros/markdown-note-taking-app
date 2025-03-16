import logging
from typing import Optional

import markdown
import models
from fastapi import Depends
from repositories.note import NoteRepository
from schemas import note_schemas, user_schemas

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
        logger.info(f"Fetching note with ID {note_id} for user {user.id}")
        note = self.note_repo.get_note(note_id, user)
        if note is None:
            logger.warning(f"Note with ID {note_id} not found for user {user.id}")
        return note

    def get_markdown_note(
        self, note_id: int, user: user_schemas.UserOut
    ) -> Optional[str]:
        logger.info(f"Fetching markdown content for note {note_id} and user {user.id}")
        note = self.get_note(note_id, user)
        if note is None:
            logger.warning(f"Markdown conversion failed: Note {note_id} not found")
            return None

        try:
            content = note.note
            html = markdown.markdown(content)
            return html
        except Exception as e:
            logger.exception(f"Error converting note {note_id} to markdown: {e}")
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
        logger.info(
            f"Fetching notes for user {user.id} with limit {limit} and page {page}"
        )
        notes, total = self.note_repo.get_notes(user, limit, page, search)
        logger.info(f"Fetched {len(notes)} notes out of {total} for user {user.id}")

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
        logger.info(f"Creating note for user {user.id}")
        new_note = self.note_repo.create_note(note, user)
        logger.info(f"Note created with ID {new_note.id} for user {user.id}")
        return new_note

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
        logger.info(f"Updating note {note_id} for user {user.id}")
        note = self.note_repo.update_note(note_id, updated_note_info, user)
        if note:
            logger.info(f"Note {note_id} updated successfully for user {user.id}")
        else:
            logger.warning(f"Failed to update note {note_id} for user {user.id}")
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
        logger.info(f"Deleting note {note_id} for user {user.id}")
        response = self.note_repo.delete_note(note_id, user)
        if response:
            logger.info(f"Note {note_id} deleted successfully for user {user.id}")
        else:
            logger.warning(f"Failed to delete note {note_id} for user {user.id}")
        return response
