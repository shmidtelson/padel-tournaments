"""Repository ports (interfaces). Implemented in infrastructure layer."""

from abc import ABC, abstractmethod
from typing import Sequence

from .entities import User, Organization, OrganizationMember, Tournament, Player, Round, Match
from .value_objects import TournamentFormat, OrgMemberRole


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: int) -> User | None:
        ...

    @abstractmethod
    async def get_by_email(self, email: str) -> User | None:
        ...

    @abstractmethod
    async def get_by_phone(self, phone: str) -> User | None:
        ...

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        ...

    @abstractmethod
    async def add(self, user: User) -> User:
        ...

    @abstractmethod
    async def save(self, user: User) -> None:
        ...


class IOrganizationRepository(ABC):
    @abstractmethod
    async def get_by_id(self, org_id: int) -> Organization | None:
        ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Organization | None:
        ...

    @abstractmethod
    async def list_by_status(self, status: str) -> Sequence[Organization]:
        ...

    @abstractmethod
    async def add(self, org: Organization) -> Organization:
        ...

    @abstractmethod
    async def save(self, org: Organization) -> None:
        ...


class IOrganizationMemberRepository(ABC):
    @abstractmethod
    async def get_member(self, user_id: int, organization_id: int) -> OrganizationMember | None:
        ...

    @abstractmethod
    async def get_org_members(self, organization_id: int) -> Sequence[OrganizationMember]:
        ...

    @abstractmethod
    async def get_organization_ids_for_user(self, user_id: int) -> Sequence[int]:
        """Organization IDs where the user is a member (any role)."""
        ...

    @abstractmethod
    async def is_user_org_admin(self, user_id: int, organization_id: int) -> bool:
        """True если пользователь — owner или admin организации."""
        ...

    @abstractmethod
    async def is_user_org_owner(self, user_id: int, organization_id: int) -> bool:
        """True если пользователь — owner организации (может добавлять админов)."""
        ...

    @abstractmethod
    async def add(self, member: OrganizationMember) -> OrganizationMember:
        ...


class ITournamentRepository(ABC):
    @abstractmethod
    async def get_by_id(self, tournament_id: int) -> Tournament | None:
        ...

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Tournament | None:
        ...

    @abstractmethod
    async def list_by_organization(self, organization_id: int) -> Sequence[Tournament]:
        ...

    @abstractmethod
    async def add(self, tournament: Tournament) -> Tournament:
        ...

    @abstractmethod
    async def save(self, tournament: Tournament) -> None:
        ...


class IPlayerRepository(ABC):
    @abstractmethod
    async def get_by_id(self, player_id: int) -> Player | None:
        ...

    @abstractmethod
    async def list_by_tournament(self, tournament_id: int) -> Sequence[Player]:
        ...

    @abstractmethod
    async def add(self, player: Player) -> Player:
        ...

    @abstractmethod
    async def save(self, player: Player) -> None:
        ...

    @abstractmethod
    async def save_many(self, players: Sequence[Player]) -> None:
        ...


class IRoundRepository(ABC):
    @abstractmethod
    async def get_by_id(self, round_id: int) -> Round | None:
        ...

    @abstractmethod
    async def list_by_tournament(self, tournament_id: int) -> Sequence[Round]:
        ...

    @abstractmethod
    async def add(self, round_entity: Round) -> Round:
        ...


class IMatchRepository(ABC):
    @abstractmethod
    async def get_by_id(self, match_id: int) -> Match | None:
        ...

    @abstractmethod
    async def list_by_round(self, round_id: int) -> Sequence[Match]:
        ...

    @abstractmethod
    async def add(self, match: Match) -> Match:
        ...

    @abstractmethod
    async def add_many(self, matches: Sequence[Match]) -> None:
        ...

    @abstractmethod
    async def save(self, match: Match) -> None:
        ...
