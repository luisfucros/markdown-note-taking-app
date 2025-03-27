from __future__ import annotations as _annotations

import json
import os
from contextvars import ContextVar
from typing import Optional
from urllib.parse import urljoin

import requests
from agents import (
    function_tool,
)

jwt_token: ContextVar[Optional[str]] = ContextVar("jwt_token", default=None)


class JWTTokenManager:
    """Context manager for handling JWT tokens in a context variable."""

    def __init__(self, token: str):
        self.token = token
        self.token_context = None

    def __enter__(self):
        self.token_context = jwt_token.set(self.token)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token_context is not None:
            jwt_token.reset(self.token_context)


@function_tool
def get_note(note_id: int) -> Optional[str]:
    """
    Get a note by its ID.

    Args:
        note_id: The ID of the note to retrieve
        token: Authentication token

    Returns:
        The note information

    Raises:
        requests.HTTPError: If the request fails
    """
    url = urljoin(os.getenv("NOTES_URL", ""), f"notes/{note_id}")
    headers = {"Content-Type": "application/json"}
    token = jwt_token.get()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, headers=headers)
    try:
        response.raise_for_status()
        return json.dumps(response.json()) if response.content else None
    except requests.exceptions.HTTPError as http_err:
        return json.dumps(
            {
                "error": f"HTTP error occurred: {http_err}",
                "status_code": response.status_code,
            }
        )
    except requests.exceptions.RequestException as req_err:
        return json.dumps({"error": f"Request error occurred: {req_err}"})


@function_tool
def get_notes(limit: int = 10, page: int = 1, search: str = "") -> Optional[str]:
    """
    Get a list of notes with pagination and optional search.

    Args:
        token: Authentication token
        limit: Maximum number of notes to return (max 10)
        page: Page number of results
        search: Optional search query

    Returns:
        A response containing the notes and pagination information

    Raises:
        requests.HTTPError: If the request fails
    """
    url = urljoin(os.getenv("NOTES_URL", ""), "notes")
    params = {"limit": limit, "page": page, "search": search}
    headers = {"Content-Type": "application/json"}
    token = jwt_token.get()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.get(url, params=params, headers=headers)
    try:
        response.raise_for_status()
        return json.dumps(response.json()) if response.content else None
    except requests.exceptions.HTTPError as http_err:
        return json.dumps(
            {
                "error": f"HTTP error occurred: {http_err}",
                "status_code": response.status_code,
            }
        )
    except requests.exceptions.RequestException as req_err:
        return json.dumps({"error": f"Request error occurred: {req_err}"})


@function_tool
def create_note(title: str, note: str) -> Optional[str]:
    """
    Create a new note.

    Args:
        note: The note data to create
        token: Authentication token

    Returns:
        The created note information

    Raises:
        requests.HTTPError: If the request fails
    """
    url = urljoin(os.getenv("NOTES_URL", ""), "notes")
    data = {"title": title, "note": note}
    headers = {"Content-Type": "application/json"}
    token = jwt_token.get()
    headers["Authorization"] = f"Bearer {token}"
    response = requests.post(url, json=data, headers=headers)
    try:
        response.raise_for_status()
        return json.dumps(response.json()) if response.content else None
    except requests.exceptions.HTTPError as http_err:
        return json.dumps(
            {
                "error": f"HTTP error occurred: {http_err}",
                "status_code": response.status_code,
            }
        )
    except requests.exceptions.RequestException as req_err:
        return json.dumps({"error": f"Request error occurred: {req_err}"})
