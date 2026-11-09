"""Authentication routes."""

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestFormfrom app.api.deps import CurrentUser, UserSvcfrom app.core.exceptions import AuthenticationError
from app.core.security import (
    create_access_token,
    create_refresh_token,    verify_token,)from app.schemas.token import RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserRead

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserSvc,) -> Any:
    """OAuth2 compatible token login.

    Returns access token and refresh token.
    Raises domain exceptions handled by exception handlers.
    """
    user = await user_service.authenticate(form_data.username, form_data.password)
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    user_service: UserSvc,
) -> Any:
    """Register a new user.

    Raises AlreadyExistsError if email is already registered.
    """
    user = await user_service.register(user_in)
    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
    user_service: UserSvc,) -> Any:
    """Get new access token using refresh token.

    Raises AuthenticationError if refresh token is invalid or expired.
    """
    # No DB-backed sessions — validate the refresh JWT directly.
    payload = verify_token(body.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise AuthenticationError(message="Invalid or expired refresh token")
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationError(message="Invalid refresh token")
    user = await user_service.get_by_id(user_id)    if not user.is_active:
        raise AuthenticationError(message="User account is disabled")

    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))    return Token(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def logout(
    body: RefreshTokenRequest,) -> None:    """No-op without session tracking. Clients drop their JWTs locally."""
    return None

@router.get("/me", response_model=UserRead)
async def get_current_user_info(current_user: CurrentUser) -> Any:
    """Get current authenticated user information."""
    return current_user