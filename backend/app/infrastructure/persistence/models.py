"""SQLAlchemy ORM models (infrastructure). Map to domain entities in repositories."""

from datetime import datetime
from sqlalchemy import String, ForeignKey, Enum, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.domain.value_objects import TournamentFormat, OrgMemberRole, OrganizationStatus


class SiteSettingModel(Base):
    __tablename__ = "site_settings"

    key: Mapped[str] = mapped_column(String(128), primary_key=True)
    value: Mapped[str] = mapped_column(String(2048), nullable=False, default="")


class BlogPostModel(Base):
    __tablename__ = "blog_posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    body: Mapped[str] = mapped_column(String(100000), nullable=False)  # HTML or Markdown
    locale: Mapped[str] = mapped_column(String(10), nullable=False, default="ru")
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(32), unique=True, index=True, nullable=True)
    telegram_id: Mapped[str | None] = mapped_column(String(64), unique=True, index=True, nullable=True)
    first_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization_memberships = relationship("OrganizationMemberModel", back_populates="user", cascade="all, delete-orphan")


class OrganizationModel(Base):
    __tablename__ = "organizations"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrganizationStatus.pending.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    plan: Mapped[str] = mapped_column(String(32), nullable=False, default="free")  # free | pro

    members = relationship("OrganizationMemberModel", back_populates="organization", cascade="all, delete-orphan")
    tournaments = relationship("TournamentModel", back_populates="organization", cascade="all, delete-orphan")


class OrganizationMemberModel(Base):
    __tablename__ = "organization_members"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[OrgMemberRole] = mapped_column(Enum(OrgMemberRole), nullable=False, default=OrgMemberRole.admin)

    user = relationship("UserModel", back_populates="organization_memberships")
    organization = relationship("OrganizationModel", back_populates="members")


class TournamentModel(Base):
    __tablename__ = "tournaments"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    format: Mapped[TournamentFormat] = mapped_column(Enum(TournamentFormat), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    points_per_round: Mapped[int | None] = mapped_column(Integer, nullable=True)
    pairing_strategy: Mapped[str | None] = mapped_column(String(32), nullable=True)  # random | by_ranking | similar_points_avoid_rematch
    status: Mapped[str] = mapped_column(String(32), default="draft")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("OrganizationModel", back_populates="tournaments")
    players = relationship("PlayerModel", back_populates="tournament", cascade="all, delete-orphan", order_by="PlayerModel.id")
    rounds = relationship("RoundModel", back_populates="tournament", cascade="all, delete-orphan", order_by="RoundModel.round_index")


class PlayerModel(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    total_points: Mapped[int] = mapped_column(Integer, default=0)

    tournament = relationship("TournamentModel", back_populates="players")


class RoundModel(Base):
    __tablename__ = "rounds"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tournament_id: Mapped[int] = mapped_column(ForeignKey("tournaments.id", ondelete="CASCADE"), nullable=False)
    round_index: Mapped[int] = mapped_column(Integer, nullable=False)

    tournament = relationship("TournamentModel", back_populates="rounds")
    matches = relationship("MatchModel", back_populates="round", cascade="all, delete-orphan")


class MatchModel(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    round_id: Mapped[int] = mapped_column(ForeignKey("rounds.id", ondelete="CASCADE"), nullable=False)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player3_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player4_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    score_team1: Mapped[int | None] = mapped_column(Integer, nullable=True)
    score_team2: Mapped[int | None] = mapped_column(Integer, nullable=True)

    round = relationship("RoundModel", back_populates="matches")
