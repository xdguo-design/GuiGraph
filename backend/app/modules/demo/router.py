"""演示/测试数据模块。

提供一键种子数据接口，便于本地演示与冒烟测试：
  - 创建虚拟用户
  - 维护组织结构（公司 → 部门 → 团队）
  - 维护人员-团队-角色绑定
  - 灌入变更/构建/升级等看板数据
  - 个人/团队看板汇总
"""

import random
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.core.security.crypto import hash_password
from app.modules.user.models import SysUser
from app.shared.enums import LoginMethod, UserStatus, ChangeStatus, UpgradeStatus

router = APIRouter()


# ── 种子数据配置 ──

VIRTUAL_USERS = [
    # 系统管理员
    {"username": "admin", "password": "admin123", "nickname": "系统管理员", "role": "system_admin", "team": None},
    # 各团队成员
    {"username": "alice", "password": "alice123", "nickname": "Alice (前端组)", "role": "editor", "team": "FE"},
    {"username": "bob",   "password": "bob123",   "nickname": "Bob (前端组)",   "role": "editor", "team": "FE"},
    {"username": "carol", "password": "carol123", "nickname": "Carol (后端组)", "role": "editor", "team": "BE"},
    {"username": "david", "password": "david123", "nickname": "David (后端组)", "role": "team_admin", "team": "BE"},
    {"username": "evan",  "password": "evan123",  "nickname": "Evan (测试组)",  "role": "editor", "team": "QA"},
    {"username": "frank", "password": "frank123", "nickname": "Frank (运维组)", "role": "dept_admin", "team": "OPS"},
    {"username": "viewer","password": "viewer123","nickname": "查看者",         "role": "viewer", "team": "FE"},
]

ORG_TREE = [
    {
        "name": "示例科技公司", "code": "DEMO",
        "children": [
            {
                "name": "研发中心", "code": "RD",
                "children": [
                    {"name": "前端组", "code": "FE"},
                    {"name": "后端组", "code": "BE"},
                    {"name": "测试组", "code": "QA"},
                ],
            },
            {
                "name": "基础架构", "code": "INFRA",
                "children": [
                    {"name": "运维组", "code": "OPS"},
                ],
            },
        ],
    },
]

CHANGE_TITLES = [
    ("优化登录页加载性能", "API", "REQUIREMENT"),
    ("修复用户中心头像上传失败", "CODE", "BUG_FIX"),
    ("升级 PostgreSQL 到 15.4", "DB", "TECH_DEBT"),
    ("新增组织架构权限校验", "API", "REQUIREMENT"),
    ("Jenkins 流水线并发数调整", "INFRA", "PERFORMANCE"),
    ("完善审计日志记录", "CODE", "COMPLIANCE"),
    ("前端构建迁移到 Vite 5", "CODE", "TECH_DEBT"),
    ("变更详情页支持 Markdown", "CODE", "REQUIREMENT"),
    ("优化 Git 分支刷新接口", "API", "PERFORMANCE"),
    ("修复移动端样式错位", "CODE", "BUG_FIX"),
    ("新增 AI 助手 MCP 集成", "API", "REQUIREMENT"),
    ("Dashboard 看板卡片化重构", "CODE", "TECH_DEBT"),
]


@router.post("/seed")
async def seed_demo_data(current_user: SysUser = Depends(get_current_user)):
    """一键灌入演示数据：虚拟用户 + 组织 + 人员权限 + 变更记录。"""
    from app.core.database.session import AsyncSessionLocal
    from app.modules.organization.models import SysCompany, BizDepartment, BizTeam, BizTeamMember
    from app.modules.change.models import BizChangeItem
    from app.modules.upgrade.models import SysUpgradeLog
    from app.shared.enums import ChangeType, ChangeReason

    created = {"users": 0, "org": 0, "members": 0, "changes": 0, "upgrades": 0}

    async with AsyncSessionLocal() as session:
        # 1. 灌入虚拟用户
        for u in VIRTUAL_USERS:
            exists = await session.execute(select(SysUser).where(SysUser.username == u["username"]))
            if exists.scalar_one_or_none():
                continue
            user = SysUser(
                username=u["username"],
                nickname=u["nickname"],
                password_hash=hash_password(u["password"]),
                login_method=LoginMethod.PASSWORD,
                status=UserStatus.ACTIVE,
            )
            session.add(user)
            created["users"] += 1
        await session.flush()

        # 2. 灌入组织
        for comp_data in ORG_TREE:
            exists = await session.execute(select(SysCompany).where(SysCompany.code == comp_data["code"]))
            if exists.scalar_one_or_none():
                continue
            comp = SysCompany(name=comp_data["name"], code=comp_data["code"])
            session.add(comp)
            await session.flush()
            created["org"] += 1
            for dept_data in comp_data.get("children", []):
                dept = BizDepartment(
                    name=dept_data["name"], code=dept_data["code"],
                    company_id=comp.id, created_by=current_user.id,
                )
                session.add(dept)
                await session.flush()
                created["org"] += 1
                for team_data in dept_data.get("children", []):
                    team = BizTeam(
                        name=team_data["name"], code=team_data["code"],
                        department_id=dept.id, created_by=current_user.id,
                    )
                    session.add(team)
                    await session.flush()
                    created["org"] += 1

        await session.flush()

        # 3. 维护人员-团队关系
        user_rows = await session.execute(select(SysUser))
        users = {u.username: u for u in user_rows.scalars().all()}
        team_rows = await session.execute(select(BizTeam))
        teams = {t.code: t for t in team_rows.scalars().all()}

        for u in VIRTUAL_USERS:
            if not u["team"]:
                continue
            user = users.get(u["username"])
            team = teams.get(u["team"])
            if not user or not team:
                continue
            exists = await session.execute(
                select(BizTeamMember).where(
                    BizTeamMember.team_id == team.id,
                    BizTeamMember.user_id == user.id,
                )
            )
            if exists.scalar_one_or_none():
                continue
            # 团队内角色：把 system_admin/dept_admin/team_admin 映射为 admin，其余为 member
            internal_role = "admin" if u["role"] in ("system_admin", "dept_admin", "team_admin") else "member"
            session.add(BizTeamMember(team_id=team.id, user_id=user.id, role=internal_role))
            created["members"] += 1

        # 4. 灌入变更记录
        change_count = await session.execute(select(BizChangeItem))
        if not change_count.scalars().first():
            now = datetime.utcnow()
            alice = users.get("alice")
            carol = users.get("david")  # 后端负责人
            statuses = [ChangeStatus.DRAFT, ChangeStatus.APPROVED, ChangeStatus.RELEASED, ChangeStatus.ROLLED_BACK]
            fe_team = teams.get("FE")
            be_team = teams.get("BE")
            qa_team = teams.get("QA")
            ops_team = teams.get("OPS")
            team_pool = [t for t in (fe_team, be_team, qa_team, ops_team) if t]
            for i, (title, ctype, reason) in enumerate(CHANGE_TITLES):
                # 偶数交给 Alice(前)/FE；奇数交给 Carol(后)/BE；其余随机团队
                if i % 2 == 0:
                    creator = alice
                    team = fe_team
                else:
                    creator = carol
                    team = be_team
                # 每 4 条轮换一次团队，制造多团队混合效果
                if team_pool and i % 4 == 3:
                    team = team_pool[i % len(team_pool)]
                ch = BizChangeItem(
                    version_id=1,  # 默认版本
                    change_type=ChangeType(ctype.lower()),
                    content=title,
                    change_reason=ChangeReason(reason.lower()),
                    status=random.choice(statuses),
                    created_by=(creator.id if creator else current_user.id),
                    team_id=(team.id if team else None),
                    created_at=now - timedelta(days=i, hours=random.randint(0, 23)),
                )
                session.add(ch)
                created["changes"] += 1
            await session.flush()

        # 5. 灌入升级日志
        upgrade_count = await session.execute(select(SysUpgradeLog))
        if not upgrade_count.scalars().first():
            from app.shared.enums import UpgradeType
            now = datetime.utcnow()
            carol = users.get("carol")
            for i in range(6):
                up = SysUpgradeLog(
                    version_from=f"v1.{4 + i}.0",
                    version_to=f"v1.{5 + i}.0",
                    upgrade_type=random.choice(list(UpgradeType)),
                    status=random.choice([UpgradeStatus.SUCCESS, UpgradeStatus.SUCCESS, UpgradeStatus.FAILED]),
                    start_time=now - timedelta(days=i * 7),
                    end_time=now - timedelta(days=i * 7) + timedelta(minutes=random.randint(5, 60)),
                    duration_sec=random.randint(300, 3600),
                    operator_id=carol.id if carol else current_user.id,
                )
                session.add(up)
                created["upgrades"] += 1

        await session.commit()

    return Response.ok({
        "message": "演示数据灌入完成",
        "created": created,
        "virtual_users": [
            {"username": u["username"], "password": u["password"], "role": u["role"], "team": u["team"]}
            for u in VIRTUAL_USERS
        ],
    })


@router.delete("/seed")
async def clear_demo_data(current_user: SysUser = Depends(get_current_user)):
    """清空演示数据（保留 admin）。"""
    from app.core.database.session import AsyncSessionLocal
    from app.modules.organization.models import SysCompany, BizDepartment, BizTeam, BizTeamMember
    from app.modules.change.models import BizChangeItem
    from app.modules.upgrade.models import SysUpgradeLog

    removed = {"users": 0, "org": 0, "members": 0, "changes": 0, "upgrades": 0}
    virtual_names = [u["username"] for u in VIRTUAL_USERS if u["username"] != "admin"]

    async with AsyncSessionLocal() as session:
        # 先删除团队成员关系
        virtual_ids_rows = await session.execute(
            select(SysUser.id).where(SysUser.username.in_(virtual_names))
        )
        virtual_ids = [r[0] for r in virtual_ids_rows.all()]

        if virtual_ids:
            result = await session.execute(
                delete(BizTeamMember).where(BizTeamMember.user_id.in_(virtual_ids))
            )
            removed["members"] = result.rowcount or 0

        # 删除非 admin 用户
        result = await session.execute(
            delete(SysUser).where(SysUser.username.in_(virtual_names))
        )
        removed["users"] = result.rowcount or 0

        # 删除组织（自下而上）
        result = await session.execute(delete(BizTeam))
        removed["org"] += result.rowcount or 0
        result = await session.execute(delete(BizDepartment))
        removed["org"] += result.rowcount or 0
        result = await session.execute(delete(SysCompany))
        removed["org"] += result.rowcount or 0

        # 删除变更和升级
        result = await session.execute(delete(BizChangeItem))
        removed["changes"] = result.rowcount or 0
        result = await session.execute(delete(SysUpgradeLog))
        removed["upgrades"] = result.rowcount or 0

        await session.commit()

    return Response.ok({"message": "演示数据已清空", "removed": removed})


# ── 个人 / 团队看板 ──

@router.get("/kanban/personal")
async def personal_kanban(current_user: SysUser = Depends(get_current_user)):
    """个人看板：当前用户的变更/团队信息。"""
    from app.core.database.session import AsyncSessionLocal
    from app.modules.organization.models import BizTeam, BizTeamMember, BizDepartment
    from app.modules.change.models import BizChangeItem

    async with AsyncSessionLocal() as session:
        # 变更统计
        all_changes = (await session.execute(
            select(BizChangeItem).where(BizChangeItem.created_by == current_user.id)
        )).scalars().all()
        status_count = {s.value: 0 for s in ChangeStatus}
        for c in all_changes:
            status_count[c.status.value] = status_count.get(c.status.value, 0) + 1

        # 我的团队
        tm_rows = await session.execute(
            select(BizTeam, BizTeamMember, BizDepartment)
            .join(BizTeamMember, BizTeamMember.team_id == BizTeam.id)
            .join(BizDepartment, BizDepartment.id == BizTeam.department_id)
            .where(BizTeamMember.user_id == current_user.id)
        )
        my_teams = []
        for team, member, dept in tm_rows.all():
            my_teams.append({
                "team_id": str(team.id),
                "team_name": team.name,
                "team_code": team.code,
                "department": dept.name,
                "role": member.role,
            })

        # 最近 5 条变更
        recent_rows = await session.execute(
            select(BizChangeItem).where(BizChangeItem.created_by == current_user.id)
            .order_by(BizChangeItem.created_at.desc()).limit(5)
        )
        recent = [{
            "id": str(c.id),
            "title": c.content,
            "type": c.change_type.value,
            "status": c.status.value,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        } for c in recent_rows.scalars().all()]

    return Response.ok({
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "nickname": current_user.nickname,
            "status": current_user.status.value,
        },
        "stats": {
            "total_changes": len(all_changes),
            "by_status": status_count,
        },
        "teams": my_teams,
        "recent_changes": recent,
    })


@router.get("/kanban/team/{team_id}")
async def team_kanban(team_id: str, current_user: SysUser = Depends(get_current_user)):
    """团队看板：指定团队的成员/变更汇总。"""
    from app.core.database.session import AsyncSessionLocal
    from app.modules.organization.models import BizTeam, BizTeamMember, BizDepartment
    from app.modules.change.models import BizChangeItem

    async with AsyncSessionLocal() as session:
        try:
            team_id_int = int(team_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的 team_id")
        team = await session.get(BizTeam, team_id_int)
        if not team:
            raise HTTPException(status_code=404, detail="团队不存在")

        dept = await session.get(BizDepartment, team.department_id)

        # 团队成员
        members_rows = await session.execute(
            select(SysUser, BizTeamMember)
            .join(BizTeamMember, BizTeamMember.user_id == SysUser.id)
            .where(BizTeamMember.team_id == team.id)
        )
        members = [{
            "user_id": str(u.id),
            "username": u.username,
            "nickname": u.nickname,
            "team_role": m.role,
            "status": u.status.value,
        } for u, m in members_rows.all()]

        member_ids = [int(m["user_id"]) for m in members]
        change_count = {s.value: 0 for s in ChangeStatus}
        recent_changes = []
        if member_ids:
            changes_rows = await session.execute(
                select(BizChangeItem).where(BizChangeItem.created_by.in_(member_ids))
                .order_by(BizChangeItem.created_at.desc())
            )
            for c in changes_rows.scalars().all():
                change_count[c.status.value] = change_count.get(c.status.value, 0) + 1
                if len(recent_changes) < 8:
                    recent_changes.append({
                        "id": str(c.id),
                        "title": c.content,
                        "type": c.change_type.value,
                        "status": c.status.value,
                        "created_at": c.created_at.isoformat() if c.created_at else None,
                    })

    return Response.ok({
        "team": {
            "id": str(team.id),
            "name": team.name,
            "code": team.code,
            "department": dept.name if dept else None,
        },
        "stats": {
            "member_count": len(members),
            "total_changes": sum(change_count.values()),
            "by_status": change_count,
        },
        "members": members,
        "recent_changes": recent_changes,
    })


@router.get("/kanban/teams")
async def my_teams(current_user: SysUser = Depends(get_current_user)):
    """当前用户可访问的团队列表（用于团队看板切换）。"""
    from app.core.database.session import AsyncSessionLocal
    from app.modules.organization.models import BizTeam, BizTeamMember, BizDepartment

    async with AsyncSessionLocal() as session:
        rows = await session.execute(
            select(BizTeam, BizTeamMember, BizDepartment)
            .join(BizTeamMember, BizTeamMember.team_id == BizTeam.id)
            .join(BizDepartment, BizDepartment.id == BizTeam.department_id)
            .where(BizTeamMember.user_id == current_user.id)
        )
        result = [{
            "team_id": str(t.id),
            "team_name": t.name,
            "team_code": t.code,
            "department": d.name,
        } for t, _, d in rows.all()]
    return Response.ok({"teams": result})
