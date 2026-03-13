"""Application service: organization CRUD and membership. Подтверждение организации — только суперпользователь."""

from app.domain.entities import Organization, OrganizationMember, User
from app.domain.repositories import IOrganizationRepository, IOrganizationMemberRepository, IUserRepository
from app.domain.value_objects import OrgMemberRole, OrganizationStatus


class OrganizationApplicationService:
    def __init__(
        self,
        org_repo: IOrganizationRepository,
        member_repo: IOrganizationMemberRepository,
        user_repo: IUserRepository | None = None,
    ):
        self._orgs = org_repo
        self._members = member_repo
        self._users = user_repo

    def _ensure_superuser(self, user: User | None) -> None:
        if not user or not user.is_superuser:
            raise PermissionError("Only a superuser can confirm organizations")

    async def create_organization(self, user_id: int, name: str, slug: str | None = None) -> Organization:
        slug = slug or name.lower().replace(" ", "-")[:100]
        org = Organization(id=0, name=name, slug=slug, status=OrganizationStatus.pending.value)
        org = await self._orgs.add(org)
        member = OrganizationMember(id=0, user_id=user_id, organization_id=org.id, role=OrgMemberRole.owner)
        await self._members.add(member)
        return org

    async def get_organization(self, org_id: int) -> Organization | None:
        return await self._orgs.get_by_id(org_id)

    async def list_organizations_for_user(self, user_id: int) -> list[Organization]:
        org_ids = await self._members.get_organization_ids_for_user(user_id)
        result = []
        for oid in org_ids:
            org = await self._orgs.get_by_id(oid)
            if org:
                result.append(org)
        return result

    async def approve_organization(self, superuser_id: int, org_id: int) -> Organization:
        if not self._users:
            raise PermissionError("Superuser check not available")
        user = await self._users.get_by_id(superuser_id)
        self._ensure_superuser(user)
        org = await self._orgs.get_by_id(org_id)
        if not org:
            raise ValueError("Organization not found")
        org.status = OrganizationStatus.approved.value
        await self._orgs.save(org)
        return org

    async def reject_organization(self, superuser_id: int, org_id: int) -> Organization:
        if not self._users:
            raise PermissionError("Superuser check not available")
        user = await self._users.get_by_id(superuser_id)
        self._ensure_superuser(user)
        org = await self._orgs.get_by_id(org_id)
        if not org:
            raise ValueError("Organization not found")
        org.status = OrganizationStatus.rejected.value
        await self._orgs.save(org)
        return org

    async def list_pending_organizations(self, superuser_id: int) -> list[Organization]:
        if not self._users:
            raise PermissionError("Superuser check not available")
        user = await self._users.get_by_id(superuser_id)
        self._ensure_superuser(user)
        return await self._orgs.list_by_status(OrganizationStatus.pending.value)

    async def add_member(self, inviter_user_id: int, org_id: int, new_user_id: int, role: OrgMemberRole) -> OrganizationMember:
        """Добавить участника в организацию. Только Owner может добавлять; можно добавить только Admin (или второго Owner)."""
        if not await self._members.is_user_org_owner(inviter_user_id, org_id):
            raise PermissionError("Only the organization Owner can add members")
        if role not in (OrgMemberRole.admin, OrgMemberRole.owner):
            raise ValueError("Role must be admin or owner")
        existing = await self._members.get_member(new_user_id, org_id)
        if existing:
            raise ValueError("User is already a member of this organization")
        org = await self._orgs.get_by_id(org_id)
        if not org:
            raise ValueError("Organization not found")
        member = OrganizationMember(id=0, user_id=new_user_id, organization_id=org_id, role=role)
        return await self._members.add(member)

    async def list_org_members(self, user_id: int, org_id: int) -> list[OrganizationMember]:
        """Список участников организации. Доступен любому члену организации (owner/admin)."""
        if not await self._members.is_user_org_admin(user_id, org_id):
            raise PermissionError("Not a member of this organization")
        return await self._members.get_org_members(org_id)
