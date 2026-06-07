"""用户管理路由（管理员）— 用于维护用户与团队的绑定关系。"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.user.models import SysUser, SysUserApplication
from app.modules.organization.models import BizTeam, BizTeamMember
from app.shared.enums import UserStatus, ApplicationStatus

router = APIRouter()


@router.get("/list")
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """列出所有用户（含团队绑定关系）。"""
    users = (await db.execute(select(SysUser))).scalars().all()
    result = []
    for u in users:
        # 查用户所属团队
        team_rows = (await db.execute(
            select(BizTeam, BizTeamMember)
            .join(BizTeamMember, BizTeamMember.team_id == BizTeam.id)
            .where(BizTeamMember.user_id == u.id)
        )).all()
        teams = [{
            "team_id": str(t.id),
            "team_name": t.name,
            "team_code": t.code,
            "team_role": m.role,
        } for t, m in team_rows]
        # 查最近审核通过申请中分配的角色
        role = "editor"
        if u.username in ("admin", "guoxudong"):
            role = "system_admin"
        else:
            latest_app = (await db.execute(
                select(SysUserApplication)
                .where(
                    SysUserApplication.username == u.username,
                    SysUserApplication.status == ApplicationStatus.APPROVED,
                )
                .order_by(SysUserApplication.reviewed_at.desc())
                .limit(1)
            )).scalar_one_or_none()
            if latest_app and latest_app.assigned_role:
                role = latest_app.assigned_role
        result.append({
            **u.to_dict(),
            "role": role,
            "teams": teams,
        })
    return Response.ok(result)


@router.put("/{user_id}/status")
async def update_user_status(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """启用/禁用用户。"""
    u = await db.get(SysUser, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    new_status = body.get("status")
    if new_status not in ("active", "pending", "disabled"):
        raise HTTPException(status_code=400, detail="无效的 status")
    u.status = UserStatus(new_status)
    await db.commit()
    return Response.ok({"id": str(u.id), "status": u.status.value})


@router.post("/{user_id}/teams")
async def assign_user_to_team(
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """将用户添加到团队。"""
    team_id = body.get("team_id")
    role = body.get("role", "member")
    if not team_id:
        raise HTTPException(status_code=400, detail="team_id 必填")
    u = await db.get(SysUser, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="用户不存在")
    team = await db.get(BizTeam, int(team_id))
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    exists = (await db.execute(
        select(BizTeamMember).where(
            BizTeamMember.team_id == int(team_id),
            BizTeamMember.user_id == user_id,
        )
    )).scalar_one_or_none()
    if exists:
        return Response.ok({"message": "已存在", "member": exists.to_dict()})
    m = BizTeamMember(team_id=int(team_id), user_id=user_id, role=role)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return Response.ok(m.to_dict())


@router.delete("/{user_id}/teams/{team_id}")
async def remove_user_from_team(
    user_id: int,
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """从团队移除用户。"""
    m = (await db.execute(
        select(BizTeamMember).where(
            BizTeamMember.team_id == team_id,
            BizTeamMember.user_id == user_id,
        )
    )).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="成员不存在")
    await db.delete(m)
    await db.commit()
    return Response.ok({"removed": user_id, "team_id": team_id})
