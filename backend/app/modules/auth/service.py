from datetime import datetime
import logging

from sqlalchemy import select

from app.core.database.session import AsyncSessionLocal
from app.core.security.crypto import hash_password, verify_password
from app.modules.user.models import SysUser, SysUserApplication
from app.shared.enums import LoginMethod, UserStatus, ApplicationStatus

logger = logging.getLogger(__name__)


class AuthService:

    async def authenticate_user(self, username: str, password: str) -> dict | None:
        """校验用户名密码，必须是 ACTIVE 状态才允许登录。"""
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SysUser).where(SysUser.username == username)
            )
            user = result.scalar_one_or_none()
            if not user:
                return None
            # 拒绝非激活状态的用户（待审核/禁用/锁定）
            if user.status != UserStatus.ACTIVE:
                return None
            if user.password_hash and verify_password(password, user.password_hash):
                # 优先使用用户最新一次审核通过申请中分配的角色
                role = "editor"
                app_result = await session.execute(
                    select(SysUserApplication)
                    .where(
                        SysUserApplication.username == username,
                        SysUserApplication.status == ApplicationStatus.APPROVED,
                    )
                    .order_by(SysUserApplication.reviewed_at.desc())
                    .limit(1)
                )
                latest_app = app_result.scalar_one_or_none()
                if latest_app and latest_app.assigned_role:
                    role = latest_app.assigned_role
                # 内置管理员账号（首次 ensure 创建的）默认 system_admin
                elif username in ("admin", "guoxudong"):
                    role = "system_admin"
                return {"id": str(user.id), "username": user.username, "role": role}
            return None

    async def create_user(
        self,
        username: str,
        password: str,
        nickname: str = "",
        role: str = "editor",
    ) -> dict:
        pwd_hash = hash_password(password)
        async with AsyncSessionLocal() as session:
            user = SysUser(
                username=username,
                nickname=nickname or username,
                password_hash=pwd_hash,
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return {"id": str(user.id), "username": user.username}

    async def ensure_admin_user(self, username: str, password: str, nickname: str) -> bool:
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(SysUser).where(SysUser.username == username)
            )
            user = result.scalar_one_or_none()
            if user:
                return False
            pwd_hash = hash_password(password)
            admin = SysUser(
                username=username,
                nickname=nickname,
                password_hash=pwd_hash,
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(admin)
            await session.commit()
            return True

    # ── 注册申请 ──

    async def submit_application(
        self,
        username: str,
        password: str,
        nickname: str = "",
        email: str = "",
        phone: str = "",
        reason: str = "",
    ) -> dict:
        """提交注册申请。返回新申请的 ID。"""
        async with AsyncSessionLocal() as session:
            # 检查用户名是否已存在
            existing = await session.execute(
                select(SysUser).where(SysUser.username == username)
            )
            if existing.scalar_one_or_none():
                raise ValueError("用户名已存在")
            # 检查是否有进行中的申请
            existing_app = await session.execute(
                select(SysUserApplication).where(
                    SysUserApplication.username == username,
                    SysUserApplication.status == ApplicationStatus.PENDING,
                )
            )
            if existing_app.scalar_one_or_none():
                raise ValueError("该用户名已有待审核的申请")

            app = SysUserApplication(
                username=username,
                password_hash=hash_password(password),
                nickname=nickname or username,
                email=email or None,
                phone=phone or None,
                reason=reason or None,
                status=ApplicationStatus.PENDING,
            )
            session.add(app)
            await session.commit()
            await session.refresh(app)
            return {"id": str(app.id), "username": app.username}

    async def list_applications(
        self,
        status_filter: str | None = None,
    ) -> list[dict]:
        """列出注册申请。"""
        async with AsyncSessionLocal() as session:
            stmt = select(SysUserApplication).order_by(SysUserApplication.created_at.desc())
            if status_filter:
                stmt = stmt.where(SysUserApplication.status == ApplicationStatus(status_filter))
            result = await session.execute(stmt)
            apps = result.scalars().all()
            return [a.to_dict() for a in apps]

    async def approve_application(
        self,
        application_id: int,
        reviewer_id: int,
        role: str,
        company_id: str = "",
        department_id: str = "",
        team_id: str = "",
        comment: str = "",
    ) -> dict:
        """审核通过：创建用户并分配角色/组织。"""
        from app.modules.organization.models import BizTeam, BizTeamMember

        async with AsyncSessionLocal() as session:
            app = await session.get(SysUserApplication, application_id)
            if not app:
                raise ValueError("申请不存在")
            if app.status != ApplicationStatus.PENDING:
                raise ValueError(f"该申请已处理（当前状态：{app.status.value}）")

            # 再次确认用户名未被占用（极端情况）
            existing = await session.execute(
                select(SysUser).where(SysUser.username == app.username)
            )
            if existing.scalar_one_or_none():
                raise ValueError("用户名已被占用")

            # 创建用户
            new_user = SysUser(
                username=app.username,
                nickname=app.nickname or app.username,
                email=app.email,
                phone=app.phone,
                password_hash=app.password_hash,
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(new_user)
            await session.flush()

            # 如果分配了团队，同时创建团队成员关系
            if team_id:
                try:
                    team_int_id = int(team_id)
                except (TypeError, ValueError):
                    team_int_id = None
                if team_int_id:
                    team = await session.get(BizTeam, team_int_id)
                    if team:
                        # 根据 role 决定团队内身份
                        internal_role = "admin" if role in (
                            "system_admin", "dept_admin", "team_admin"
                        ) else "member"
                        # 防止重复添加
                        exists_m = await session.execute(
                            select(BizTeamMember).where(
                                BizTeamMember.team_id == team.id,
                                BizTeamMember.user_id == new_user.id,
                            )
                        )
                        if not exists_m.scalar_one_or_none():
                            session.add(BizTeamMember(
                                team_id=team.id,
                                user_id=new_user.id,
                                role=internal_role,
                            ))

            # 更新申请单
            app.status = ApplicationStatus.APPROVED
            app.reviewed_by = reviewer_id
            app.reviewed_at = datetime.utcnow()
            app.review_comment = comment or None
            app.assigned_role = role
            app.assigned_company_id = company_id or None
            app.assigned_department_id = department_id or None
            app.assigned_team_id = team_id or None

            await session.commit()
            return {
                "id": str(app.id),
                "user_id": str(new_user.id),
                "username": new_user.username,
                "role": role,
            }

    async def reject_application(
        self,
        application_id: int,
        reviewer_id: int,
        comment: str = "",
    ) -> dict:
        """审核拒绝。"""
        async with AsyncSessionLocal() as session:
            app = await session.get(SysUserApplication, application_id)
            if not app:
                raise ValueError("申请不存在")
            if app.status != ApplicationStatus.PENDING:
                raise ValueError(f"该申请已处理（当前状态：{app.status.value}）")
            app.status = ApplicationStatus.REJECTED
            app.reviewed_by = reviewer_id
            app.reviewed_at = datetime.utcnow()
            app.review_comment = comment or None
            await session.commit()
            return {"id": str(app.id), "status": app.status.value}

    async def logout(self, user_id: str, token: str) -> None:
        logger.info(f"用户退出: {user_id}")


auth_service = AuthService()
