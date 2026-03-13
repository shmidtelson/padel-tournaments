"""Blog: публичный список и пост по slug; админ CRUD в admin.py или отдельно."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.infrastructure.api.schemas import BlogPostResponse
from app.infrastructure.persistence.models import BlogPostModel

router = APIRouter(prefix="/blog", tags=["blog"])


def _post_to_response(m: BlogPostModel) -> BlogPostResponse:
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


@router.get("", response_model=list[BlogPostResponse])
async def list_posts(
    session: Annotated[AsyncSession, Depends(get_db)],
    locale: str | None = None,
):
    """Список опубликованных постов (published_at не null), опционально по locale."""
    q = select(BlogPostModel).where(BlogPostModel.published_at.isnot(None)).order_by(BlogPostModel.published_at.desc())
    if locale:
        q = q.where(BlogPostModel.locale == locale)
    result = await session.execute(q)
    rows = result.scalars().all()
    return [_post_to_response(r) for r in rows]


@router.get("/{slug}", response_model=BlogPostResponse)
async def get_post(
    slug: str,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Один пост по slug (только опубликованный)."""
    q = select(BlogPostModel).where(BlogPostModel.slug == slug, BlogPostModel.published_at.isnot(None))
    result = await session.execute(q)
    row = result.scalars().first()
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    return _post_to_response(row)
