"""Auth API routes."""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.auth_service import AuthApplicationService
from app.core.security import create_access_token, create_refresh_token
from app.infrastructure.api.dependencies import get_auth_service
from app.infrastructure.api.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(
    body: RegisterRequest,
    auth: Annotated[AuthApplicationService, Depends(get_auth_service)],
):
    try:
        user = await auth.register_email(
            email=body.email,
            password=body.password,
            first_name=body.first_name,
            last_name=body.last_name,
        )
        return TokenResponse(
            access_token=create_access_token(user.id),
            refresh_token=create_refresh_token(user.id),
        )
    except ValueError as e:
        logger.info("register_failed email=%s reason=%s", body.email, e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    auth: Annotated[AuthApplicationService, Depends(get_auth_service)],
):
    try:
        result = await auth.login_email(email=body.email, password=body.password)
        return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)
    except ValueError as e:
        logger.info("login_failed email=%s", body.email)
        raise HTTPException(status_code=401, detail=str(e)) from e


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    body: RefreshRequest,
    auth: Annotated[AuthApplicationService, Depends(get_auth_service)],
):
    try:
        result = await auth.refresh_tokens(body.refresh_token)
        return TokenResponse(access_token=result.access_token, refresh_token=result.refresh_token)
    except ValueError as e:
        logger.info("refresh_failed reason=%s", e)
        raise HTTPException(status_code=401, detail=str(e)) from e
