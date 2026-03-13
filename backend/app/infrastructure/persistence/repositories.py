"""Repository implementations (infrastructure). Map ORM <-> domain entities."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    Match,
    Organization,
    OrganizationMember,
    Player,
    Round,
    Tournament,
    User,
)
from app.domain.repositories import (
    IMatchRepository,
    IOrganizationMemberRepository,
    IOrganizationRepository,
    IPlayerRepository,
    IRoundRepository,
    ITournamentRepository,
    IUserRepository,
)
from app.domain.value_objects import OrganizationStatus, OrgMemberRole

from .models import (
    MatchModel,
    OrganizationMemberModel,
    OrganizationModel,
    PlayerModel,
    RoundModel,
    TournamentModel,
    UserModel,
)


def _user_to_entity(m: UserModel) -> User:
    return User(
        id=m.id,
        email=m.email,
        phone=m.phone,
        telegram_id=m.telegram_id,
        first_name=m.first_name,
        last_name=m.last_name,
        password_hash=m.password_hash,
        is_superuser=getattr(m, "is_superuser", False),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _org_to_entity(m: OrganizationModel) -> Organization:
    return Organization(
        id=m.id,
        name=m.name,
        slug=m.slug,
        status=getattr(m, "status", OrganizationStatus.pending.value),
        created_at=m.created_at,
        updated_at=m.updated_at,
        plan=getattr(m, "plan", "free"),
    )


def _member_to_entity(m: OrganizationMemberModel) -> OrganizationMember:
    return OrganizationMember(
        id=m.id, user_id=m.user_id, organization_id=m.organization_id, role=m.role, created_at=None
    )


def _tournament_to_entity(m: TournamentModel) -> Tournament:
    return Tournament(
        id=m.id,
        organization_id=m.organization_id,
        name=m.name,
        format=m.format,
        slug=m.slug,
        status=m.status,
        points_per_round=m.points_per_round,
        pairing_strategy=getattr(m, "pairing_strategy", None),
        created_at=m.created_at,
        updated_at=m.updated_at,
    )


def _player_to_entity(m: PlayerModel) -> Player:
    return Player(
        id=m.id,
        tournament_id=m.tournament_id,
        first_name=m.first_name,
        last_name=m.last_name,
        user_id=m.user_id,
        total_points=m.total_points,
    )


def _round_to_entity(m: RoundModel) -> Round:
    return Round(id=m.id, tournament_id=m.tournament_id, round_index=m.round_index)


def _match_to_entity(m: MatchModel) -> Match:
    return Match(
        id=m.id,
        round_id=m.round_id,
        player1_id=m.player1_id,
        player2_id=m.player2_id,
        player3_id=m.player3_id,
        player4_id=m.player4_id,
        score_team1=m.score_team1,
        score_team2=m.score_team2,
    )


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, user_id: int) -> User | None:
        r = await self._session.get(UserModel, user_id)
        return _user_to_entity(r) if r else None

    async def get_by_email(self, email: str) -> User | None:
        q = select(UserModel).where(UserModel.email == email)
        r = (await self._session.execute(q)).scalars().first()
        return _user_to_entity(r) if r else None

    async def get_by_phone(self, phone: str) -> User | None:
        q = select(UserModel).where(UserModel.phone == phone)
        r = (await self._session.execute(q)).scalars().first()
        return _user_to_entity(r) if r else None

    async def get_by_telegram_id(self, telegram_id: str) -> User | None:
        q = select(UserModel).where(UserModel.telegram_id == telegram_id)
        r = (await self._session.execute(q)).scalars().first()
        return _user_to_entity(r) if r else None

    async def add(self, user: User) -> User:
        m = UserModel(
            email=user.email,
            password_hash=user.password_hash,
            phone=user.phone,
            telegram_id=user.telegram_id,
            first_name=user.first_name,
            last_name=user.last_name,
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _user_to_entity(m)

    async def save(self, user: User) -> None:
        m = await self._session.get(UserModel, user.id)
        if m:
            m.email = user.email
            m.phone = user.phone
            m.telegram_id = user.telegram_id
            m.first_name = user.first_name
            m.last_name = user.last_name
            m.password_hash = user.password_hash
            m.is_superuser = user.is_superuser
            await self._session.flush()


class OrganizationRepository(IOrganizationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, org_id: int) -> Organization | None:
        r = await self._session.get(OrganizationModel, org_id)
        return _org_to_entity(r) if r else None

    async def get_by_slug(self, slug: str) -> Organization | None:
        q = select(OrganizationModel).where(OrganizationModel.slug == slug)
        r = (await self._session.execute(q)).scalars().first()
        return _org_to_entity(r) if r else None

    async def list_by_status(self, status: str) -> list[Organization]:
        q = select(OrganizationModel).where(OrganizationModel.status == status)
        rows = (await self._session.execute(q)).scalars().all()
        return [_org_to_entity(r) for r in rows]

    async def add(self, org: Organization) -> Organization:
        m = OrganizationModel(
            name=org.name, slug=org.slug, status=org.status, plan=getattr(org, "plan", "free")
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _org_to_entity(m)

    async def save(self, org: Organization) -> None:
        m = await self._session.get(OrganizationModel, org.id)
        if m:
            m.name = org.name
            m.slug = org.slug
            m.status = org.status
            if hasattr(org, "plan"):
                m.plan = org.plan
            await self._session.flush()


class OrganizationMemberRepository(IOrganizationMemberRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_member(self, user_id: int, organization_id: int) -> OrganizationMember | None:
        q = select(OrganizationMemberModel).where(
            OrganizationMemberModel.user_id == user_id,
            OrganizationMemberModel.organization_id == organization_id,
        )
        r = (await self._session.execute(q)).scalars().first()
        return _member_to_entity(r) if r else None

    async def get_org_members(self, organization_id: int) -> list[OrganizationMember]:
        q = select(OrganizationMemberModel).where(
            OrganizationMemberModel.organization_id == organization_id
        )
        rows = (await self._session.execute(q)).scalars().all()
        return [_member_to_entity(r) for r in rows]

    async def get_organization_ids_for_user(self, user_id: int) -> list[int]:
        q = select(OrganizationMemberModel.organization_id).where(
            OrganizationMemberModel.user_id == user_id
        )
        rows = (await self._session.execute(q)).all()
        return [r[0] for r in rows]

    async def is_user_org_admin(self, user_id: int, organization_id: int) -> bool:
        m = await self.get_member(user_id, organization_id)
        return m is not None and m.role in (OrgMemberRole.owner, OrgMemberRole.admin)

    async def is_user_org_owner(self, user_id: int, organization_id: int) -> bool:
        m = await self.get_member(user_id, organization_id)
        return m is not None and m.role == OrgMemberRole.owner

    async def add(self, member: OrganizationMember) -> OrganizationMember:
        m = OrganizationMemberModel(
            user_id=member.user_id, organization_id=member.organization_id, role=member.role
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _member_to_entity(m)


class TournamentRepository(ITournamentRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, tournament_id: int) -> Tournament | None:
        r = await self._session.get(TournamentModel, tournament_id)
        return _tournament_to_entity(r) if r else None

    async def get_by_slug(self, slug: str) -> Tournament | None:
        q = select(TournamentModel).where(TournamentModel.slug == slug)
        r = (await self._session.execute(q)).scalars().first()
        return _tournament_to_entity(r) if r else None

    async def list_by_organization(self, organization_id: int) -> list[Tournament]:
        q = select(TournamentModel).where(TournamentModel.organization_id == organization_id)
        rows = (await self._session.execute(q)).scalars().all()
        return [_tournament_to_entity(r) for r in rows]

    async def add(self, tournament: Tournament) -> Tournament:
        m = TournamentModel(
            organization_id=tournament.organization_id,
            name=tournament.name,
            format=tournament.format,
            slug=tournament.slug,
            status=tournament.status,
            points_per_round=tournament.points_per_round,
            pairing_strategy=tournament.pairing_strategy,
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _tournament_to_entity(m)

    async def save(self, tournament: Tournament) -> None:
        m = await self._session.get(TournamentModel, tournament.id)
        if m:
            m.name = tournament.name
            m.status = tournament.status
            m.points_per_round = tournament.points_per_round
            m.pairing_strategy = tournament.pairing_strategy
            await self._session.flush()


class PlayerRepository(IPlayerRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, player_id: int) -> Player | None:
        r = await self._session.get(PlayerModel, player_id)
        return _player_to_entity(r) if r else None

    async def list_by_tournament(self, tournament_id: int) -> list[Player]:
        q = (
            select(PlayerModel)
            .where(PlayerModel.tournament_id == tournament_id)
            .order_by(PlayerModel.id)
        )
        rows = (await self._session.execute(q)).scalars().all()
        return [_player_to_entity(r) for r in rows]

    async def add(self, player: Player) -> Player:
        m = PlayerModel(
            tournament_id=player.tournament_id,
            first_name=player.first_name,
            last_name=player.last_name,
            user_id=player.user_id,
            total_points=player.total_points,
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _player_to_entity(m)

    async def save(self, player: Player) -> None:
        m = await self._session.get(PlayerModel, player.id)
        if m:
            m.total_points = player.total_points
            m.first_name = player.first_name
            m.last_name = player.last_name
            await self._session.flush()

    async def save_many(self, players: list[Player]) -> None:
        for p in players:
            await self.save(p)


class RoundRepository(IRoundRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, round_id: int) -> Round | None:
        r = await self._session.get(RoundModel, round_id)
        return _round_to_entity(r) if r else None

    async def list_by_tournament(self, tournament_id: int) -> list[Round]:
        q = (
            select(RoundModel)
            .where(RoundModel.tournament_id == tournament_id)
            .order_by(RoundModel.round_index)
        )
        rows = (await self._session.execute(q)).scalars().all()
        return [_round_to_entity(r) for r in rows]

    async def add(self, round_entity: Round) -> Round:
        m = RoundModel(
            tournament_id=round_entity.tournament_id, round_index=round_entity.round_index
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _round_to_entity(m)


class MatchRepository(IMatchRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, match_id: int) -> Match | None:
        r = await self._session.get(MatchModel, match_id)
        return _match_to_entity(r) if r else None

    async def list_by_round(self, round_id: int) -> list[Match]:
        q = select(MatchModel).where(MatchModel.round_id == round_id)
        rows = (await self._session.execute(q)).scalars().all()
        return [_match_to_entity(r) for r in rows]

    async def add(self, match: Match) -> Match:
        m = MatchModel(
            round_id=match.round_id,
            player1_id=match.player1_id,
            player2_id=match.player2_id,
            player3_id=match.player3_id,
            player4_id=match.player4_id,
            score_team1=match.score_team1,
            score_team2=match.score_team2,
        )
        self._session.add(m)
        await self._session.flush()
        await self._session.refresh(m)
        return _match_to_entity(m)

    async def add_many(self, matches: list[Match]) -> None:
        for match in matches:
            await self.add(match)

    async def save(self, match: Match) -> None:
        m = await self._session.get(MatchModel, match.id)
        if m:
            m.score_team1 = match.score_team1
            m.score_team2 = match.score_team2
            await self._session.flush()
