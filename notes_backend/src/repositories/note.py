from typing import List, Optional, Tuple

import models
from schemas import note_schemas, user_schemas

from .base import BaseRepository


class NoteRepository(BaseRepository):
    """
    Repository class for handling database operations related to Notes.
    """

    def get_note(
        self, note_id: int, user: user_schemas.UserOut
    ) -> Optional[models.Note]:
        """
        Retrieve a specific note by its ID for a given user.

        Args:
            note_id (int): The ID of the note to retrieve.
            user (user_schemas.UserOut): The user requesting the note.

        Returns:
            models.Note: The requested note.
        """
        return self._get_user_note(note_id, user.id)

    def get_notes(
        self,
        user: user_schemas.UserOut,
        limit: int,
        page: int,
        search: Optional[str] = "",
    ) -> Tuple[List[models.Note], int]:
        """
        Retrieve a paginated list of notes for a given user and the number of totals of notes.

        Args:
            user (user_schemas.UserOut): The user whose notes are being retrieved.
            limit (int): Number of notes per page.
            page (int): The page number.
            search (Optional[str], default=""): A search term to filter notes by title.

        Returns:
            List[models.Note]: A list of notes matching the criteria.
        """
        query = self.session.query(models.Note).filter(models.Note.owner_id == user.id)

        if search:
            query = query.filter(models.Note.title.contains(search))

        total = query.count()
        notes = (
            query.order_by(models.Note.created_at.desc())
            .limit(limit)
            .offset((page - 1) * limit if page > 1 else 0)
            .all()
        )

        return notes, total

    def create_note(
        self, note: note_schemas.NoteCreate, user: user_schemas.UserOut
    ) -> models.Note:
        """
        Create a new note for a user.

        Args:
            note (note_schemas.NoteCreate): The note data to create.
            user (user_schemas.UserOut): The user creating the note.

        Returns:
            models.Note: The newly created note.
        """
        new_note = models.Note(**note.model_dump(), owner_id=user.id)
        self.session.add(new_note)
        self.session.commit()
        self.session.refresh(new_note)
        return new_note

    def update_note(
        self,
        note_id: int,
        updated_note_info: note_schemas.NoteCreate,
        user: user_schemas.UserOut,
    ) -> Optional[models.Note | bool]:
        """
        Update an existing note if the user owns it.

        Args:
            note_id (int): The ID of the note to update.
            updated_note_info (note_schemas.NoteCreate): The updated note data.
            user (user_schemas.UserOut): The user making the update request.

        Returns:
            models.Note: The updated note.
        """
        note = self._get_user_note(note_id, user.id)
        if note is None or note is False:
            return note

        self.session.query(models.Note).filter_by(id=note_id, owner_id=user.id).update(
            updated_note_info.model_dump(), synchronize_session=False
        )
        self.session.commit()
        self.session.refresh(note)
        return note

    def delete_note(self, note_id: int, user: user_schemas.UserOut) -> Optional[bool]:
        """
        Delete an existing note if the user owns it.

        Args:
            note_id (int): The ID of the note to delete.
            user (user_schemas.UserOut): The user making the deletion request.

        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        note = self._get_user_note(note_id, user.id)
        if note is None or note is False:
            return note

        self.session.delete(note)
        self.session.commit()
        return True

    def _get_user_note(
        self, note_id: int, user_id: int
    ) -> Optional[models.Note | bool]:
        note = self.session.query(models.Note).filter_by(id=note_id).one_or_none()
        if note is not None and note.owner_id != user_id:
            return False

        return (
            self.session.query(models.Note)
            .filter_by(id=note_id, owner_id=user_id)
            .one_or_none()
        )
