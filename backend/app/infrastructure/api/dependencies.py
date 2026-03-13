"""FastAPI dependencies: DB session, current user, application services."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.infrastructure.persistence.repositories import (
    UserRepository,
    OrganizationRepository,
    OrganizationMemberRepository,
    TournamentRepository,
    PlayerRepository,
    RoundRepository,
    MatchRepository,
)
from app.application.auth_service import AuthApplicationService
from app.application.tournament_service import TournamentApplicationService
from app.application.organization_service import OrganizationApplicationService

security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


async def get_current_user_id(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> int | None:
    if not credentials:
        return None
    payload = decode_token(credentials.credentials)
    if not payload or payload.get("type") != "access":
        return None
    try:
        return int(payload["sub"])
    except (ValueError, KeyError):
        return None


async def require_current_user_id(
    user_id: Annotated[int | None, Depends(get_current_user_id)],
) -> int:
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user_id


async def require_superuser(
    user_id: Annotated[int, Depends(require_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db)],
) -> int:
    from app.infrastructure.persistence.repositories import UserRepository
    repo = UserRepository(session)
    user = await repo.get_by_id(user_id)
    if not user or not user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser required")
    return user_id


def get_auth_service(session: Annotated[AsyncSession, Depends(get_db)]) -> AuthApplicationService:
    return AuthApplicationService(UserRepository(session))


def get_tournament_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> TournamentApplicationService:
    return TournamentApplicationService(
        tournament_repo=TournamentRepository(session),
        player_repo=PlayerRepository(session),
        round_repo=RoundRepository(session),
        match_repo=MatchRepository(session),
        org_member_repo=OrganizationMemberRepository(session),
        org_repo=OrganizationRepository(session),
    )


def get_organization_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrganizationApplicationService:
    return OrganizationApplicationService(
        org_repo=OrganizationRepository(session),
        member_repo=OrganizationMemberRepository(session),
        user_repo=UserRepository(session),
    )
