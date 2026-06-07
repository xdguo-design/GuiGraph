"""看板/时间线路由：聚合当前用户可见的变更/升级数据。"""
from datetime import date, datetime, timedelta
import hashlib

from fastapi import APIRouter, Depends, Request, Query
from sqlalchemy import select, func, true, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.security.jwt import verify_token
from app.core.utils.response import Response
from app.modules.change.models import BizChangeItem
from app.modules.organization.models import BizTeam, BizTeamMember
from app.modules.upgrade.models import SysUpgradeLog
from app.modules.user.models import SysUser
from app.shared.enums import ChangeStatus

router = APIRouter()


# 团队默认色（与系统中其他色形成对比，确保在深色/浅色背景上都可读）
_TEAM_DEFAULT_PALETTE = [
    "#3b82f6",  # 蓝
    "#10b981",  # 翠绿
    "#f59e0b",  # 琥珀
    "#ef4444",  # 红
    "#8b5cf6",  # 紫
    "#06b6d4",  # 青
    "#ec4899",  # 粉
    "#84cc16",  # 青柠
    "#f97316",  # 橙
    "#14b8a6",  # 蓝绿
]


def _team_color(team_id: int, explicit: str | None) -> str:
    """根据团队 ID 与显式 color 计算最终色；未设置则从调色板取一个。"""
    if explicit:
        return explicit
    return _TEAM_DEFAULT_PALETTE[team_id % len(_TEAM_DEFAULT_PALETTE)]


def _user_role_from_request(request: Request) -> str:
    """从 Authorization 头中解析当前用户角色（管理员可见全量数据）。"""
    auth = request.headers.get("authorization", "")
    if not auth.lower().startswith("bearer "):
        return "editor"
    token = auth.split(" ", 1)[1]
    payload = verify_token(token) or {}
    return payload.get("role", "editor")


@router.get("")
async def get_dashboard(
    request: Request,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户的仪表盘数据。

    管理员（system_admin / dept_admin / team_admin）查看全量变更；
    普通用户仅查看自己创建的变更。
    """
    user_id = current_user.id
    role = _user_role_from_request(request)
    is_admin = role in ("system_admin", "dept_admin", "team_admin")

    scope_filter = true() if is_admin else (BizChangeItem.created_by == user_id)

    # 各状态数量
    stats_result = await db.execute(
        select(BizChangeItem.status, func.count(BizChangeItem.id))
        .where(scope_filter)
        .group_by(BizChangeItem.status)
    )
    by_status = {s.value: 0 for s in ChangeStatus}
    for status, count in stats_result.all():
        by_status[status.value if hasattr(status, "value") else status] = count

    # 总变更
    total_changes = sum(by_status.values())

    # 最近变更（5 条）
    recent_result = await db.execute(
        select(BizChangeItem)
        .where(scope_filter)
        .order_by(BizChangeItem.created_at.desc())
        .limit(5)
    )
    recent_changes = [
        {
            "id": str(c.id),
            "title": c.content[:60],
            "type": c.change_type.value if hasattr(c.change_type, "value") else c.change_type,
            "status": c.status.value if hasattr(c.status, "value") else c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in recent_result.scalars().all()
    ]

    # 升级日志统计
    upgrade_total_result = await db.execute(select(func.count(SysUpgradeLog.id)))
    upgrade_total = upgrade_total_result.scalar() or 0

    return Response.ok({
        "stats": {
            "total_changes": total_changes,
            "pending_changes": by_status.get(ChangeStatus.DRAFT.value, 0) + by_status.get(ChangeStatus.APPROVED.value, 0),
            "approved_changes": by_status.get(ChangeStatus.APPROVED.value, 0),
            "released_changes": by_status.get(ChangeStatus.RELEASED.value, 0),
            "rolled_back_changes": by_status.get(ChangeStatus.ROLLED_BACK.value, 0),
            "rejected_changes": by_status.get(ChangeStatus.REJECTED.value, 0),
            "draft_changes": by_status.get(ChangeStatus.DRAFT.value, 0),
            "by_status": by_status,
            "upgrade_logs": upgrade_total,
        },
        "recent_changes": recent_changes,
        "scope": "all" if is_admin else "mine",
    })


@router.get("/timeline")
async def get_timeline(
    func_point_id: str = "",
    version_id: str = "",
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取时间线。"""
    return Response.ok({"items": []})


# ── 看板日历 ──


def _parse_month(month_str: str) -> tuple[date, date]:
    """解析 YYYY-MM，返回当月第一天与下月第一天。"""
    y, m = month_str.split("-")
    yi, mi = int(y), int(m)
    start = date(yi, mi, 1)
    if mi == 12:
        end = date(yi + 1, 1, 1)
    else:
        end = date(yi, mi + 1, 1)
    return start, end


@router.get("/kanban")
async def get_kanban(
    request: Request,
    month: str = Query(..., description="月份，格式 YYYY-MM"),
    team_id: str = Query("", description="按团队过滤（可选）"),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取看板日历数据：返回团队、变更条目（按天聚合）、热力图统计。"""
    user_id = current_user.id
    role = _user_role_from_request(request)
    is_admin = role in ("system_admin", "dept_admin", "team_admin")

    try:
        month_start, month_end = _parse_month(month)
    except (ValueError, TypeError):
        return Response.error("月份格式错误，应为 YYYY-MM", code="BAD_REQUEST")

    # 1) 团队列表：管理员看全量；普通用户看自己所在的团队
    team_query = select(BizTeam).order_by(BizTeam.id.asc())
    if not is_admin:
        team_query = team_query.join(
            BizTeamMember, BizTeamMember.team_id == BizTeam.id
        ).where(BizTeamMember.user_id == user_id)
    teams_result = await db.execute(team_query)
    teams = [
        {
            "id": str(t.id),
            "name": t.name,
            "code": t.code,
            "color": _team_color(t.id, t.color),
        }
        for t in teams_result.scalars().all()
    ]
    team_id_to_info = {t["id"]: t for t in teams}

    # 2) 变更条目：管理员全量；普通用户仅自己创建的
    change_query = (
        select(BizChangeItem)
        .where(
            BizChangeItem.created_at >= datetime.combine(month_start, datetime.min.time()),
            BizChangeItem.created_at < datetime.combine(month_end, datetime.min.time()),
        )
        .order_by(BizChangeItem.created_at.asc())
    )
    if not is_admin:
        change_query = change_query.where(BizChangeItem.created_by == user_id)
    if team_id:
        try:
            change_query = change_query.where(BizChangeItem.team_id == int(team_id))
        except ValueError:
            pass
    changes_result = await db.execute(change_query)
    changes_rows = changes_result.scalars().all()

    # 3) 补齐 team_id：若变更未填，从创建人主团队取
    creator_team_cache: dict[int, int | None] = {}
    items_by_day: dict[str, list[dict]] = {}
    for c in changes_rows:
        team_info = None
        tid = c.team_id
        if tid is None and not is_admin:
            # 普通用户通常只属于一个团队，可直接关联
            tid_int = creator_team_cache.get(c.created_by)
            if tid_int is None and c.created_by:
                m_result = await db.execute(
                    select(BizTeamMember.team_id)
                    .where(BizTeamMember.user_id == c.created_by)
                    .order_by(BizTeamMember.id.asc())
                    .limit(1)
                )
                tid_int = m_result.scalar_one_or_none()
                creator_team_cache[c.created_by] = tid_int
            tid = tid_int
        elif tid is None and is_admin:
            # 管理员视角：若变更无 team_id，则按创建人主团队推断
            tid_int = creator_team_cache.get(c.created_by)
            if tid_int is None and c.created_by:
                m_result = await db.execute(
                    select(BizTeamMember.team_id)
                    .where(BizTeamMember.user_id == c.created_by)
                    .order_by(BizTeamMember.id.asc())
                    .limit(1)
                )
                tid_int = m_result.scalar_one_or_none()
                creator_team_cache[c.created_by] = tid_int
            tid = tid_int
        if tid is not None:
            team_info = team_id_to_info.get(str(tid))

        day_key = c.created_at.strftime("%Y-%m-%d") if c.created_at else None
        if not day_key:
            continue
        item = {
            "id": str(c.id),
            "content": c.content or "",
            "change_type": c.change_type.value if hasattr(c.change_type, "value") else c.change_type,
            "status": c.status.value if hasattr(c.status, "value") else c.status,
            "created_at": c.created_at.isoformat() if c.created_at else None,
            "team_id": str(tid) if tid is not None else None,
            "team_name": team_info["name"] if team_info else None,
            "team_color": team_info["color"] if team_info else None,
        }
        items_by_day.setdefault(day_key, []).append(item)

    # 4) 月度热力（近 12 个月，每月变更总数）
    heatmap_end = month_end
    heatmap_start = (month_start - timedelta(days=365)).replace(day=1)
    heatmap_query = (
        select(
            func.strftime("%Y-%m", BizChangeItem.created_at).label("ym"),
            func.count(BizChangeItem.id).label("cnt"),
        )
        .where(
            BizChangeItem.created_at >= datetime.combine(heatmap_start, datetime.min.time()),
            BizChangeItem.created_at < datetime.combine(heatmap_end, datetime.min.time()),
        )
        .group_by("ym")
    )
    if not is_admin:
        heatmap_query = heatmap_query.where(BizChangeItem.created_by == user_id)
    heatmap_rows = (await db.execute(heatmap_query)).all()
    heatmap = [{"month": ym, "count": cnt} for ym, cnt in heatmap_rows]

    return Response.ok({
        "month": month,
        "teams": teams,
        "items_by_day": items_by_day,
        "heatmap": heatmap,
    })
