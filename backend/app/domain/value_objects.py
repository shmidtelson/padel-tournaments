"""Domain value objects and enums."""

from enum import Enum


class TournamentFormat(str, Enum):
    americano = "americano"
    mexicano = "mexicano"
    round_robin = "round_robin"
    single_elimination = "single_elimination"
    double_elimination = "double_elimination"


class OrgMemberRole(str, Enum):
    owner = "owner"
    admin = "admin"


class TournamentStatus(str, Enum):
    draft = "draft"
    published = "published"
    in_progress = "in_progress"
    completed = "completed"


class OrganizationStatus(str, Enum):
    """Организация создаётся в статусе pending; суперпользователь подтверждает (approved) или отклоняет (rejected)."""
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
