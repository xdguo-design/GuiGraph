"""变更管理模块路由。"""

from datetime import datetime

from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.change.schemas import (
    ChangeItemCreate, ChangeItemResponse, ChangeItemUpdate,
    ChangeApproveRequest,
)
from app.modules.change.models import BizChangeItem
from app.modules.change.service import change_service
from app.modules.knowledge.service import knowledge_service
from app.modules.user.models import SysUser
from app.modules.organization.models import BizTeam
from app.shared.enums import ChangeType, ChangeStatus, ChangeReason

router = APIRouter()


def _serialize_change(item: BizChangeItem) -> dict:
    """将 ORM 实体序列化为统一响应结构。"""
    return {
        "id": str(item.id),
        "version_id": str(item.version_id),
        "change_type": item.change_type.value if hasattr(item.change_type, "value") else item.change_type,
        "content": item.content,
        "effect_scope": item.effect_scope,
        "change_reason": item.change_reason.value if hasattr(item.change_reason, "value") else item.change_reason,
        "change_reason_detail": item.change_reason_detail,
        "related_requirement_no": item.related_requirement_no,
        "func_point_ids": item.func_point_ids,
        "img_list": item.img_list,
        "file_ref": item.file_ref,
        "impact_tables": item.impact_tables,
        "impact_apis": item.impact_apis,
        "related_incidents": item.related_incidents,
        "rag_doc_id": item.rag_doc_id,
        "git_repo_id": str(item.git_repo_id) if item.git_repo_id else None,
        "git_branch_source": item.git_branch_source,
        "git_branch_target": item.git_branch_target,
        "git_merge_commit": item.git_merge_commit,
        "jenkins_build_id": item.jenkins_build_id,
        "status": item.status.value if hasattr(item.status, "value") else item.status,
        "team_id": str(item.team_id) if item.team_id else None,
        "created_by": str(item.created_by),
        "approved_by": str(item.approved_by) if item.approved_by else None,
        "approved_at": item.approved_at.isoformat() if item.approved_at else None,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
    }


async def _sync_to_knowledge(db: AsyncSession, change: BizChangeItem):
    """变更审批通过后，自动同步内容到团队知识库。"""
    if not change.team_id:
        return

    team = await db.get(BizTeam, change.team_id)
    team_name = team.name if team else None
    kb = await knowledge_service.get_or_create_team_knowledge_base(db, change.team_id, team_name)
    kb_id = int(kb["id"])

    from app.modules.knowledge.models import Note
    result = await db.execute(select(Note).where(Note.knowledge_base_id == kb_id))
    existing_notes = result.scalars().all()
    existing_note = next(
        (n for n in existing_notes if n.related_change_ids and str(change.id) in n.related_change_ids),
        None,
    )

    change_type_label = change.change_type.value if hasattr(change.change_type, "value") else str(change.change_type)
    content_parts = [f"## 变更内容\n{change.content}"]
    if change.effect_scope:
        content_parts.append(f"\n## 影响范围\n{change.effect_scope}")
    if change.change_reason_detail:
        content_parts.append(f"\n## 变更原因补充\n{change.change_reason_detail}")

    title_prefix = {"db": "数据库", "api": "API", "config": "配置", "code": "代码", "infra": "基础设施"}.get(
        change_type_label, change_type_label
    )
    title = f"[{title_prefix}] {change.content[:80]}"
    reason_label = change.change_reason.value if hasattr(change.change_reason, "value") else str(change.change_reason)

    if existing_note:
        tags = list(set((existing_note.tags or []) + [change_type_label, reason_label]))
        update_data = {"title": title, "content": "\n".join(content_parts), "tags": tags}
        if existing_note.related_change_ids and str(change.id) not in existing_note.related_change_ids:
            update_data["related_change_ids"] = existing_note.related_change_ids + [str(change.id)]
        await knowledge_service.update_note(db, existing_note.id, update_data, change.created_by)
    else:
        note_data = {
            "knowledge_base_id": kb_id,
            "title": title,
            "content": "\n".join(content_parts),
            "tags": [change_type_label, reason_label],
            "related_change_ids": [str(change.id)],
            "author_id": change.created_by,
            "is_published": True,
        }
        await knowledge_service.create_note(db, note_data)


@router.get("")
async def list_changes(
    page: int = 1,
    page_size: int = 20,
    change_type: str = "",
    status: str = "",
    team_id: str = "",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """查询变更列表。"""
    # 构建查询条件
    conditions = []
    if change_type:
        try:
            conditions.append(BizChangeItem.change_type == ChangeType(change_type))
        except ValueError:
            pass  # 无效的变更类型，忽略
    if status:
        try:
            conditions.append(BizChangeItem.status == ChangeStatus(status))
        except ValueError:
            pass  # 无效的状态，忽略
    if team_id:
        try:
            conditions.append(BizChangeItem.team_id == int(team_id))
        except ValueError:
            pass  # 无效的团队ID，忽略

    # 查询总数
    count_query = select(func.count(BizChangeItem.id))
    if conditions:
        count_query = count_query.where(and_(*conditions))
    total_result = await db.execute(count_query)
    total = (total_result.scalar() or 0)

    # 查询分页数据
    query = select(BizChangeItem).order_by(BizChangeItem.created_at.desc())
    if conditions:
        query = query.where(and_(*conditions))
    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    items = result.scalars().all()

    # 转换为响应格式
    items_data = [_serialize_change(item) for item in items]

    total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return Response.ok({
        "items": items_data,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    })


@router.get("/{change_id}")
async def get_change(
    change_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取变更详情。"""
    try:
        id_int = int(change_id)
    except ValueError:
        return Response.fail("无效的变更ID", code="INVALID_ID")

    item = await db.get(BizChangeItem, id_int)
    if not item:
        return Response.fail("变更不存在", code="NOT_FOUND")

    return Response.ok(_serialize_change(item))


@router.post("")
async def create_change(
    body: ChangeItemCreate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """创建变更申请：持久化到 biz_change_item 表。"""
    try:
        version_id_int = int(body.version_id)
    except (TypeError, ValueError):
        return Response.fail("无效的版本 ID", code="INVALID_VERSION_ID")

    item = BizChangeItem(
        version_id=version_id_int,
        change_type=body.change_type,
        content=body.content,
        effect_scope=body.effect_scope,
        change_reason=body.change_reason,
        change_reason_detail=body.change_reason_detail,
        related_requirement_no=body.related_requirement_no,
        func_point_ids=body.func_point_ids,
        img_list=body.img_list,
        file_ref=body.file_ref,
        team_id=body.team_id,
        status=ChangeStatus.DRAFT,
        created_by=current_user.id,
    )
    db.add(item)
    await db.flush()
    await db.commit()
    await db.refresh(item)
    return Response.ok(_serialize_change(item))


@router.put("/{change_id}")
async def update_change(
    change_id: str,
    body: ChangeItemUpdate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新变更：持久化字段到 biz_change_item 表。"""
    try:
        id_int = int(change_id)
    except ValueError:
        return Response.fail("无效的变更ID", code="INVALID_ID")

    item = await db.get(BizChangeItem, id_int)
    if not item:
        return Response.fail("变更不存在", code="NOT_FOUND")

    if item.status != ChangeStatus.DRAFT:
        return Response.fail("仅草稿状态可编辑", code="INVALID_STATUS")

    update_data = body.model_dump(exclude_unset=True)
    for k, v in update_data.items():
        if hasattr(item, k) and k not in ("id", "created_by", "created_at"):
            setattr(item, k, v)
    await db.commit()
    await db.refresh(item)
    return Response.ok(_serialize_change(item))


@router.post("/{change_id}/approve")
async def approve_change(
    change_id: str,
    body: ChangeApproveRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """审批变更：更新状态 + 写入审批人/时间。"""
    try:
        id_int = int(change_id)
    except ValueError:
        return Response.fail("无效的变更ID", code="INVALID_ID")

    item = await db.get(BizChangeItem, id_int)
    if not item:
        return Response.fail("变更不存在", code="NOT_FOUND")

    if item.status not in (ChangeStatus.DRAFT, ChangeStatus.APPROVED):
        return Response.fail("当前状态不允许审批", code="INVALID_STATUS")

    item.status = ChangeStatus.APPROVED if body.approved else ChangeStatus.REJECTED
    item.approved_by = current_user.id
    item.approved_at = datetime.utcnow()
    if body.comment:
        item.change_reason_detail = (
            (item.change_reason_detail or "") + f"\n[审批意见] {body.comment}"
        ).strip()
    await db.flush()

    # 审批通过时，自动同步变更内容到团队知识库
    if body.approved:
        try:
            await _sync_to_knowledge(db, item)
        except Exception as e:
            logger.warning(f"同步到知识库失败 (change_id={id_int}): {e}")

    await db.commit()
    await db.refresh(item)
    return Response.ok(_serialize_change(item))
