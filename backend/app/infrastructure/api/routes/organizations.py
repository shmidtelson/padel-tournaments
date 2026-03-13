"""Organization API routes. Подтверждение организации — только суперпользователь."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.application.organization_service import OrganizationApplicationService
from app.domain.value_objects import OrgMemberRole
from app.infrastructure.api.dependencies import (
    get_organization_service,
    require_current_user_id,
    require_superuser,
)
from app.infrastructure.api.schemas import (
    AddOrganizationMemberRequest,
    CreateOrganizationRequest,
    OrganizationApprovalRequest,
    OrganizationMemberResponse,
    OrganizationResponse,
)

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.post("", response_model=OrganizationResponse)
async def create_organization(
    body: CreateOrganizationRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    try:
        org = await svc.create_organization(user_id, body.name, body.slug)
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            status=org.status,
            plan=getattr(org, "plan", "free"),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("", response_model=list[OrganizationResponse])
async def list_organizations(
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    orgs = await svc.list_organizations_for_user(user_id)
    return [
        OrganizationResponse(
            id=o.id, name=o.name, slug=o.slug, status=o.status, plan=getattr(o, "plan", "free")
        )
        for o in orgs
    ]


@router.get("/pending", response_model=list[OrganizationResponse])
async def list_pending_organizations(
    _superuser_id: Annotated[int, Depends(require_superuser)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    """Список организаций, ожидающих подтверждения. Только для суперпользователя."""
    try:
        orgs = await svc.list_pending_organizations(_superuser_id)
        return [
            OrganizationResponse(
                id=o.id, name=o.name, slug=o.slug, status=o.status, plan=getattr(o, "plan", "free")
            )
            for o in orgs
        ]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.patch("/{org_id}/approval", response_model=OrganizationResponse)
async def set_organization_approval(
    org_id: int,
    body: OrganizationApprovalRequest,
    superuser_id: Annotated[int, Depends(require_superuser)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    """Подтвердить или отклонить организацию. Только суперпользователь."""
    try:
        if body.approved:
            org = await svc.approve_organization(superuser_id, org_id)
        else:
            org = await svc.reject_organization(superuser_id, org_id)
        return OrganizationResponse(
            id=org.id,
            name=org.name,
            slug=org.slug,
            status=org.status,
            plan=getattr(org, "plan", "free"),
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{org_id}", response_model=OrganizationResponse)
async def get_organization(
    org_id: int,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    org = await svc.get_organization(org_id)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        status=org.status,
        plan=getattr(org, "plan", "free"),
    )


@router.get("/{org_id}/members", response_model=list[OrganizationMemberResponse])
async def list_organization_members(
    org_id: int,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    """Список участников организации (owner и admin). Доступен любому члену организации."""
    try:
        members = await svc.list_org_members(user_id, org_id)
        return [
            OrganizationMemberResponse(
                id=m.id, user_id=m.user_id, organization_id=m.organization_id, role=m.role.value
            )
            for m in members
        ]
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e


@router.post("/{org_id}/members", response_model=OrganizationMemberResponse)
async def add_organization_member(
    org_id: int,
    body: AddOrganizationMemberRequest,
    user_id: Annotated[int, Depends(require_current_user_id)],
    svc: Annotated[OrganizationApplicationService, Depends(get_organization_service)],
):
    """Добавить участника в организацию (Admin или Owner). Только текущий Owner организации может добавлять."""
    try:
        role = OrgMemberRole(body.role) if body.role in ("owner", "admin") else None
        if not role:
            raise HTTPException(status_code=400, detail="role must be 'owner' or 'admin'")
        member = await svc.add_member(user_id, org_id, body.user_id, role)
        return OrganizationMemberResponse(
            id=member.id,
            user_id=member.user_id,
            organization_id=member.organization_id,
            role=member.role.value,
        )
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
