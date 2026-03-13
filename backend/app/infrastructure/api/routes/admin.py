"""Admin API (только SuperAdmin): настройки сайта и статистика."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.api.dependencies import require_superuser
from datetime import datetime
from app.infrastructure.api.schemas import (
    SiteSettingsResponse,
    SiteSettingsUpdateRequest,
    AdminStatsResponse,
    BlogPostResponse,
    BlogPostCreateRequest,
    BlogPostUpdateRequest,
)
from app.infrastructure.persistence.models import (
    SiteSettingModel,
    UserModel,
    OrganizationModel,
    TournamentModel,
    PlayerModel,
    RoundModel,
    MatchModel,
    BlogPostModel,
)

router = APIRouter(prefix="/admin", tags=["admin"])

# Рекомендуемые ключи настроек (описания для UI)
SETTING_KEYS = {
    "maintenance_mode": "Режим техобслуживания (true/false)",
    "registration_enabled": "Открыта ли регистрация (true/false)",
    "default_locale": "Язык по умолчанию (ru/en)",
    "max_tournaments_per_month_free": "Макс. турниров в месяц на бесплатном тарифе",
    "max_organizations_per_user": "Макс. организаций у одного пользователя",
    "site_name": "Название сайта",
    "contact_email": "Email для обратной связи",
}


@router.get("/settings", response_model=SiteSettingsResponse)
async def get_site_settings(
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить все настройки сайта (только SuperAdmin)."""
    result = await session.execute(select(SiteSettingModel))
    rows = result.scalars().all()
    settings = {r.key: r.value for r in rows}
    # Подставить дефолты для известных ключей, если их ещё нет
    for key, _ in SETTING_KEYS.items():
        if key not in settings:
            if key == "maintenance_mode":
                settings[key] = "false"
            elif key == "registration_enabled":
                settings[key] = "true"
            elif key == "default_locale":
                settings[key] = "ru"
            elif key == "max_tournaments_per_month_free":
                settings[key] = "3"
            elif key == "max_organizations_per_user":
                settings[key] = "10"
            elif key == "site_name":
                settings[key] = "Padel Tournaments"
            elif key == "contact_email":
                settings[key] = ""
    return SiteSettingsResponse(settings=settings)


@router.patch("/settings", response_model=SiteSettingsResponse)
async def update_site_settings(
    body: SiteSettingsUpdateRequest,
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Обновить настройки сайта (только SuperAdmin). Передаются только изменяемые ключи."""
    for key, value in body.settings.items():
        if len(key) > 128:
            raise HTTPException(status_code=400, detail=f"Key too long: {key}")
        if len(str(value)) > 2048:
            raise HTTPException(status_code=400, detail=f"Value too long for key: {key}")
        stmt = select(SiteSettingModel).where(SiteSettingModel.key == key)
        r = await session.execute(stmt)
        row = r.scalars().first()
        if row:
            row.value = str(value)
        else:
            session.add(SiteSettingModel(key=key, value=str(value)))
    await session.commit()
    # Return full settings
    result = await session.execute(select(SiteSettingModel))
    rows = result.scalars().all()
    settings = {r.key: r.value for r in rows}
    defaults = {
        "maintenance_mode": "false",
        "registration_enabled": "true",
        "default_locale": "ru",
        "max_tournaments_per_month_free": "3",
        "max_organizations_per_user": "10",
        "site_name": "Padel Tournaments",
        "contact_email": "",
    }
    for key in SETTING_KEYS:
        if key not in settings:
            settings[key] = defaults.get(key, "")
    return SiteSettingsResponse(settings=settings)


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Статистика по платформе: пользователи, организации, турниры, игроки, раунды, матчи (только SuperAdmin)."""
    users_total = (await session.execute(select(func.count()).select_from(UserModel))).scalar() or 0
    users_superusers = (
        await session.execute(select(func.count()).select_from(UserModel).where(UserModel.is_superuser.is_(True)))
    ).scalar() or 0
    organizations_total = (await session.execute(select(func.count()).select_from(OrganizationModel))).scalar() or 0
    organizations_pending = (
        await session.execute(
            select(func.count()).select_from(OrganizationModel).where(OrganizationModel.status == "pending")
        )
    ).scalar() or 0
    organizations_approved = (
        await session.execute(
            select(func.count()).select_from(OrganizationModel).where(OrganizationModel.status == "approved")
        )
    ).scalar() or 0
    organizations_rejected = (
        await session.execute(
            select(func.count()).select_from(OrganizationModel).where(OrganizationModel.status == "rejected")
        )
    ).scalar() or 0
    tournaments_total = (await session.execute(select(func.count()).select_from(TournamentModel))).scalar() or 0
    players_total = (await session.execute(select(func.count()).select_from(PlayerModel))).scalar() or 0
    rounds_total = (await session.execute(select(func.count()).select_from(RoundModel))).scalar() or 0
    matches_total = (await session.execute(select(func.count()).select_from(MatchModel))).scalar() or 0

    return AdminStatsResponse(
        users_total=users_total,
        users_superusers=users_superusers,
        organizations_total=organizations_total,
        organizations_pending=organizations_pending,
        organizations_approved=organizations_approved,
        organizations_rejected=organizations_rejected,
        tournaments_total=tournaments_total,
        players_total=players_total,
        rounds_total=rounds_total,
        matches_total=matches_total,
    )


# ----- Admin Blog CRUD -----
def _blog_post_to_response(m: BlogPostModel) -> BlogPostResponse:
    return BlogPostResponse(
        id=m.id,
        slug=m.slug,
        title=m.title,
        body=m.body,
        locale=m.locale or "ru",
        published_at=m.published_at.isoformat() if m.published_at else None,
        created_at=m.created_at.isoformat() if m.created_at else "",
        updated_at=m.updated_at.isoformat() if m.updated_at else "",
    )


@router.get("/blog", response_model=list[BlogPostResponse])
async def admin_list_blog_posts(
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
    locale: str | None = None,
):
    """Список всех постов (включая черновики)."""
    q = select(BlogPostModel).order_by(BlogPostModel.created_at.desc())
    if locale:
        q = q.where(BlogPostModel.locale == locale)
    result = await session.execute(q)
    rows = result.scalars().all()
    return [_blog_post_to_response(r) for r in rows]


@router.post("/blog", response_model=BlogPostResponse)
async def admin_create_blog_post(
    body: BlogPostCreateRequest,
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Создать пост (черновик или с published_at)."""
    r = (await session.execute(select(BlogPostModel).where(BlogPostModel.slug == body.slug))).scalars().first()
    if r:
        raise HTTPException(status_code=400, detail="Slug already exists")
    published_at = None
    if body.published_at:
        try:
            published_at = datetime.fromisoformat(body.published_at.replace("Z", "+00:00"))
        except ValueError:
            pass
    m = BlogPostModel(
        slug=body.slug,
        title=body.title,
        body=body.body,
        locale=body.locale or "ru",
        published_at=published_at,
    )
    session.add(m)
    await session.commit()
    await session.refresh(m)
    return _blog_post_to_response(m)


@router.patch("/blog/{post_id}", response_model=BlogPostResponse)
async def admin_update_blog_post(
    post_id: int,
    body: BlogPostUpdateRequest,
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Обновить пост."""
    m = (await session.get(BlogPostModel, post_id))
    if not m:
        raise HTTPException(status_code=404, detail="Post not found")
    if body.slug is not None:
        m.slug = body.slug
    if body.title is not None:
        m.title = body.title
    if body.body is not None:
        m.body = body.body
    if body.locale is not None:
        m.locale = body.locale
    if body.published_at is not None:
        if body.published_at == "":
            m.published_at = None
        else:
            try:
                m.published_at = datetime.fromisoformat(body.published_at.replace("Z", "+00:00"))
            except ValueError:
                pass
    await session.commit()
    await session.refresh(m)
    return _blog_post_to_response(m)


@router.delete("/blog/{post_id}", status_code=204)
async def admin_delete_blog_post(
    post_id: int,
    _user_id: Annotated[int, Depends(require_superuser)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Удалить пост."""
    m = await session.get(BlogPostModel, post_id)
    if not m:
        raise HTTPException(status_code=404, detail="Post not found")
    await session.delete(m)
    await session.commit()
