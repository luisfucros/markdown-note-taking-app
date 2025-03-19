from typing import Optional

from authentication import oauth2
from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    Query,
    Response,
    UploadFile,
    status,
)
from fastapi.responses import HTMLResponse
from schemas import note_schemas, user_schemas
from services.note import NoteService

router = APIRouter(prefix="/notes", tags=["Notes"])


@router.get("/{id}", response_model=note_schemas.NoteOut)
def get_note(
    id: int,
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    note = service.get_note(id, current_user)
    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Note with id: {id} was not found",
        )
    return note


@router.get("/markdown/{id}", response_class=HTMLResponse)
def get_markdown_note(
    id: int,
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    try:
        note = service.get_markdown_note(id, current_user)
        if note is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Note with id: {id} was not found",
            )
        return note
    except HTTPException as e:
        raise e
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get("", response_model=note_schemas.NoteResponse)
def get_notes(
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
    limit: int = Query(10, le=10),
    page: int = Query(1, ge=1),
    search: Optional[str] = "",
    service: NoteService = Depends(),
):
    return service.get_notes(current_user, limit, page, search)


@router.post(
    "", status_code=status.HTTP_201_CREATED, response_model=note_schemas.NoteOut
)
def create_note(
    note: note_schemas.NoteCreate,
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    return service.create_note(user=current_user, note=note)


@router.post("/markdown")
async def upload_markdown_file(
    file: UploadFile = File(...),
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    if file.filename is not None and not file.filename.endswith(".md"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only markdown files are allowed. Please upload a valid .md file.",
        )
    try:
        file_content = await file.read()
        markdown_text = file_content.decode("utf-8")
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Empty or corrupt file."
        )

    mark_down_note = note_schemas.NoteCreate(title=file.filename, note=markdown_text)
    new_note = service.create_note(user=current_user, note=mark_down_note)
    return new_note


@router.put("/{id}", response_model=note_schemas.NoteOut)
def update_note(
    id: int,
    updated_note_info: note_schemas.NoteCreate,
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    updated_note = service.update_note(
        note_id=id, updated_note_info=updated_note_info, user=current_user
    )
    if updated_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    if updated_note is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )
    return updated_note


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    id: int,
    service: NoteService = Depends(),
    current_user: user_schemas.UserOut = Depends(oauth2.get_current_user),
):
    response = service.delete_note(id, current_user)
    if response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found",
        )
    if response is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
