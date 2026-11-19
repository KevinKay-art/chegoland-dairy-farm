"""CSRF protection: token generation and validation using sessions."""

import secrets
from typing import Optional
from fastapi import Request


def generate_csrf_token(request: Request) -> str:
    token = secrets.token_urlsafe(32)
    request.session["_csrf_token"] = token
    return token


def validate_csrf_token(request: Request, token: str) -> bool:
    stored = request.session.get("_csrf_token")
    if not stored or stored != token:
        return False
    return True