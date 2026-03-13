"""Stripe: создание Checkout Session для тарифа Pro, webhook для подписок."""

import logging
from typing import Annotated

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.domain.value_objects import OrgMemberRole
from app.infrastructure.api.dependencies import require_current_user_id
from app.infrastructure.api.schemas import CreateCheckoutRequest
from app.infrastructure.persistence.models import OrganizationMemberModel, OrganizationModel

router = APIRouter(prefix="/billing", tags=["billing"])
logger = logging.getLogger(__name__)

if settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


def _url_allowed(url: str, base: str) -> bool:
    """True if base is empty (dev) or url starts with base (no open redirect)."""
    if not base or not base.strip():
        return True
    base_stripped = base.strip().rstrip("/")
    return (
        url.startswith(base_stripped + "/")
        or url == base_stripped
        or url.startswith(base_stripped + "?")
    )


@router.post("/create-checkout-session")
async def create_checkout_session(
    body: CreateCheckoutRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    """Создать Stripe Checkout Session для тарифа Pro. Только Owner организации."""
    if not settings.stripe_secret_key or not settings.stripe_price_id_pro:
        raise HTTPException(status_code=503, detail="Billing not configured")
    base_url = getattr(settings, "allowed_frontend_base_url", "") or ""
    if not _url_allowed(body.success_url, base_url) or not _url_allowed(body.cancel_url, base_url):
        raise HTTPException(
            status_code=400, detail="success_url and cancel_url must belong to the allowed frontend"
        )
    org_id = body.organization_id
    # Проверка: пользователь — Owner организации
    q = select(OrganizationMemberModel).where(
        OrganizationMemberModel.organization_id == org_id,
        OrganizationMemberModel.user_id == user_id,
        OrganizationMemberModel.role == OrgMemberRole.owner,
    )
    r = (await session.execute(q)).scalars().first()
    if not r:
        raise HTTPException(status_code=403, detail="Only organization Owner can subscribe")
    org = await session.get(OrganizationModel, org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    customer_id = org.stripe_customer_id
    if not customer_id:
        cust = stripe.Customer.create(
            email="",  # optional for API; set later via dashboard or update
            metadata={"organization_id": str(org_id)},
        )
        customer_id = cust.id
        org.stripe_customer_id = customer_id
        await session.commit()

    checkout = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": settings.stripe_price_id_pro, "quantity": 1}],
        success_url=body.success_url,
        cancel_url=body.cancel_url,
        metadata={"organization_id": str(org_id)},
        subscription_data={"metadata": {"organization_id": str(org_id)}},
    )
    return {"url": checkout.url, "session_id": checkout.id}


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    stripe_signature: Annotated[str | None, Header(alias="Stripe-Signature")] = None,
):
    """Webhook Stripe: обновление подписки (subscription created/updated/deleted)."""
    if not settings.stripe_webhook_secret:
        raise HTTPException(status_code=503, detail="Webhook not configured")
    payload = await request.body()
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature or "", settings.stripe_webhook_secret
        )
    except Exception:
        logger.warning("Stripe webhook signature verification failed")
        raise HTTPException(status_code=400, detail="Invalid signature") from None
    if event["type"] == "checkout.session.completed":
        sess = event["data"]["object"]
        org_id = sess.get("metadata", {}).get("organization_id") or sess.get("subscription")
        sub_id = sess.get("subscription")
        if org_id and sub_id:
            org_id = int(org_id)
            org = await session.get(OrganizationModel, org_id)
            if org:
                org.stripe_subscription_id = sub_id
                org.plan = "pro"
                await session.commit()
    elif event["type"] == "customer.subscription.updated":
        sub = event["data"]["object"]
        org_id = sub.get("metadata", {}).get("organization_id")
        if org_id:
            org = await session.get(OrganizationModel, int(org_id))
            if org:
                org.plan = "pro" if sub.get("status") in ("active", "trialing") else "free"
                if sub.get("status") not in ("active", "trialing"):
                    org.stripe_subscription_id = None
                await session.commit()
    elif event["type"] == "customer.subscription.deleted":
        sub = event["data"]["object"]
        org_id = sub.get("metadata", {}).get("organization_id")
        if org_id:
            org = await session.get(OrganizationModel, int(org_id))
            if org:
                org.plan = "free"
                org.stripe_subscription_id = None
                await session.commit()
    return {"received": True}
