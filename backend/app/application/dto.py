"""Application DTOs (commands, queries, results)."""

from collections.abc import Sequence
from dataclasses import dataclass

from app.domain.value_objects import TournamentFormat


@dataclass
class RegisterUserCommand:
    email: str | None
    password: str | None
    phone: str | None
    telegram_id: str | None
    first_name: str | None
    last_name: str | None


@dataclass
class LoginResult:
    user_id: int
    access_token: str
    refresh_token: str


@dataclass
class CreateTournamentCommand:
    organization_id: int
    name: str
    format: TournamentFormat
    points_per_round: int | None = None
    pairing_strategy: str | None = None  # random | by_ranking | similar_points_avoid_rematch


@dataclass
class AddPlayerCommand:
    tournament_id: int
    first_name: str
    last_name: str
    user_id: int | None = None


@dataclass
class UpdateMatchScoreCommand:
    match_id: int
    score_team1: int
    score_team2: int


@dataclass
class LeaderboardEntry:
    rank: int
    player_id: int
    first_name: str
    last_name: str
    total_points: int


@dataclass
class MatchDto:
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


@dataclass
class RoundDto:
    round_index: int
    matches: Sequence[MatchDto]
