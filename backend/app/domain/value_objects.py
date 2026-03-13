"""Domain value objects and enums."""

from enum import StrEnum


class TournamentFormat(StrEnum):
    americano = "americano"
    mexicano = "mexicano"
    round_robin = "round_robin"
    single_elimination = "single_elimination"
    double_elimination = "double_elimination"


class PairingStrategy(StrEnum):
    """How to form teams when generating the next round (4 players -> 2v2)."""

    random = "random"  # Full random shuffle
    by_ranking = "by_ranking"  # Weak+strong vs weak+strong (1+3 vs 2+4 by points)
    similar_points_avoid_rematch = (
        "similar_points_avoid_rematch"  # Group by similar points, minimize re-matches
    )


class OrgMemberRole(StrEnum):
    owner = "owner"
    admin = "admin"


class TournamentStatus(StrEnum):
    draft = "draft"
    published = "published"
    in_progress = "in_progress"
    completed = "completed"


class OrganizationStatus(StrEnum):
    """Организация создаётся в статусе pending; суперпользователь подтверждает (approved) или отклоняет (rejected)."""

    pending = "pending"
    approved = "approved"
    rejected = "rejected"
