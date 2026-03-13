"""Domain entities (aggregates and entities). No ORM, pure domain logic."""

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from .value_objects import OrgMemberRole, TournamentFormat

if TYPE_CHECKING:
    pass


@dataclass
class User:
    id: int
    email: str | None
    phone: str | None
    telegram_id: str | None
    first_name: str | None
    last_name: str | None
    password_hash: str | None = None
    is_superuser: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def display_name(self) -> str:
        if self.first_name or self.last_name:
            return f"{self.first_name or ''} {self.last_name or ''}".strip()
        return self.email or self.phone or str(self.id)


@dataclass
class Organization:
    id: int
    name: str
    slug: str
    status: str  # OrganizationStatus: pending / approved / rejected
    created_at: datetime | None = None
    updated_at: datetime | None = None
    plan: str = "free"  # free | pro (Stripe)

    def is_approved(self) -> bool:
        return self.status == "approved"


@dataclass
class OrganizationMember:
    id: int
    user_id: int
    organization_id: int
    role: OrgMemberRole
    created_at: datetime | None = None


@dataclass
class Tournament:
    id: int
    organization_id: int
    name: str
    format: TournamentFormat
    slug: str
    status: str  # TournamentStatus value
    points_per_round: int | None
    pairing_strategy: str | None = (
        None  # PairingStrategy value; None = use format default (random for americano, by_ranking for mexicano)
    )
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def is_americano_or_mexicano(self) -> bool:
        return self.format in (TournamentFormat.americano, TournamentFormat.mexicano)


@dataclass
class Player:
    id: int
    tournament_id: int
    first_name: str
    last_name: str
    user_id: int | None
    total_points: int

    def display_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


@dataclass
class Round:
    id: int
    tournament_id: int
    round_index: int


@dataclass
class Match:
    id: int
    round_id: int
    player1_id: int
    player2_id: int
    player3_id: int
    player4_id: int
    score_team1: int | None
    score_team2: int | None

    def team1_player_ids(self) -> tuple[int, int]:
        return (self.player1_id, self.player2_id)

    def team2_player_ids(self) -> tuple[int, int]:
        return (self.player3_id, self.player4_id)
