"""Pydantic request/response schemas (API contract)."""

from pydantic import BaseModel, EmailStr, Field
from app.domain.value_objects import TournamentFormat


# ----- Auth -----
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=256)
    first_name: str | None = None
    last_name: str | None = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=256)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


# ----- Organization -----
class CreateOrganizationRequest(BaseModel):
    name: str
    slug: str | None = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    status: str  # pending / approved / rejected
    plan: str = "free"  # free | pro


class AddOrganizationMemberRequest(BaseModel):
    user_id: int
    role: str  # "admin" | "owner"


class OrganizationMemberResponse(BaseModel):
    id: int
    user_id: int
    organization_id: int
    role: str


class OrganizationApprovalRequest(BaseModel):
    approved: bool  # True = approve, False = reject


# ----- Tournament -----
class CreateTournamentRequest(BaseModel):
    organization_id: int
    name: str
    format: TournamentFormat
    points_per_round: int | None = None


class TournamentResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    format: TournamentFormat
    slug: str
    status: str
    points_per_round: int | None

    class Config:
        from_attributes = True


class AddPlayerRequest(BaseModel):
    first_name: str
    last_name: str
    user_id: int | None = None


class PlayerResponse(BaseModel):
    id: int
    tournament_id: int
    first_name: str
    last_name: str
    user_id: int | None
    total_points: int


class UpdateMatchScoreRequest(BaseModel):
    score_team1: int
    score_team2: int


class MatchResponse(BaseModel):
    id: int
    round_index: int
    player1_id: int
    player2_id: int
    player3_id: int
    player4_id: int
    score_team1: int | None
    score_team2: int | None
    player1_name: str
    player2_name: str
    player3_name: str
    player4_name: str


class RoundResponse(BaseModel):
    round_index: int
    matches: list[MatchResponse]


class LeaderboardEntryResponse(BaseModel):
    rank: int
    player_id: int
    first_name: str
    last_name: str
    total_points: int


# ----- Admin (SuperAdmin) -----
class SiteSettingsResponse(BaseModel):
    """Настройки сайта (key-value). Рекомендуемые ключи: maintenance_mode, registration_enabled, default_locale, max_tournaments_per_month_free, max_organizations_per_user, site_name, contact_email."""
    settings: dict[str, str]


class SiteSettingsUpdateRequest(BaseModel):
    settings: dict[str, str]  # ключи и строковые значения


class AdminStatsResponse(BaseModel):
    users_total: int
    users_superusers: int
    organizations_total: int
    organizations_pending: int
    organizations_approved: int
    organizations_rejected: int
    tournaments_total: int
    players_total: int
    rounds_total: int
    matches_total: int


# ----- Blog (public + admin) -----
class BlogPostResponse(BaseModel):
    id: int
    slug: str
    title: str
    body: str
    locale: str
    published_at: str | None  # ISO datetime
    created_at: str
    updated_at: str


class BlogPostCreateRequest(BaseModel):
    slug: str
    title: str
    body: str
    locale: str = "ru"
    published_at: str | None = None  # ISO datetime, null = draft


class BlogPostUpdateRequest(BaseModel):
    slug: str | None = None
    title: str | None = None
    body: str | None = None
    locale: str | None = None
    published_at: str | None = None


# ----- Billing -----
class CreateCheckoutRequest(BaseModel):
    organization_id: int
    success_url: str
    cancel_url: str
