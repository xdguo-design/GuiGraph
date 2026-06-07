"""组织架构模块路由。

提供完整的组织架构维护与人员权限维护 API：
  - GET    /org/tree                    获取完整组织树（公司→部门→团队→成员）
  - GET    /org/companies               获取所有公司
  - POST   /org/companies               新建公司
  - PUT    /org/companies/{id}          更新公司
  - DELETE /org/companies/{id}          删除公司
  - GET    /org/departments             获取所有部门
  - POST   /org/departments             新建部门
  - PUT    /org/departments/{id}        更新部门
  - DELETE /org/departments/{id}        删除部门
  - GET    /org/teams                   获取所有团队
  - POST   /org/teams                   新建团队
  - PUT    /org/teams/{id}              更新团队
  - DELETE /org/teams/{id}              删除团队
  - GET    /org/teams/{id}/members      团队成员列表
  - POST   /org/teams/{id}/members      添加团队成员
  - PUT    /org/teams/{id}/members/{uid}  更新团队成员角色
  - DELETE /org/teams/{id}/members/{uid}  移除团队成员
  - POST   /org/upload                  上传组织结构 (JSON/CSV)
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.user.models import SysUser
from app.modules.organization.models import (
    SysCompany, BizDepartment, BizTeam, BizTeamMember
)

router = APIRouter()


# ── 公司 ──

@router.get("/companies")
async def list_companies(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """获取所有公司（含部门与团队）。"""
    rows = (await db.execute(select(SysCompany))).scalars().all()
    result = []
    for c in rows:
        depts = (await db.execute(
            select(BizDepartment).where(BizDepartment.company_id == c.id)
        )).scalars().all()
        dept_data = []
        for d in depts:
            teams = (await db.execute(
                select(BizTeam).where(BizTeam.department_id == d.id)
            )).scalars().all()
            team_data = []
            for t in teams:
                member_count = (await db.execute(
                    select(BizTeamMember).where(BizTeamMember.team_id == t.id)
                )).scalars().all()
                team_data.append({
                    **t.to_dict(),
                    "member_count": len(member_count),
                })
            dept_data.append({**d.to_dict(), "teams": team_data})
        result.append({**c.to_dict(), "departments": dept_data})
    return Response.ok(result)


@router.post("/companies")
async def create_company(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """创建公司。"""
    name = body.get("name")
    code = body.get("code")
    if not name or not code:
        raise HTTPException(status_code=400, detail="name 和 code 不能为空")
    exists = (await db.execute(select(SysCompany).where(SysCompany.code == code))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=f"编码 {code} 已存在")
    c = SysCompany(name=name, code=code)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return Response.ok({**c.to_dict(), "departments": []})


@router.put("/companies/{company_id}")
async def update_company(
    company_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """更新公司。"""
    c = await db.get(SysCompany, company_id)
    if not c:
        raise HTTPException(status_code=404, detail="公司不存在")
    if "name" in body and body["name"]:
        c.name = body["name"]
    if "code" in body and body["code"]:
        c.code = body["code"]
    await db.commit()
    return Response.ok(c.to_dict())


@router.delete("/companies/{company_id}")
async def delete_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """删除公司（级联删除部门与团队）。"""
    c = await db.get(SysCompany, company_id)
    if not c:
        raise HTTPException(status_code=404, detail="公司不存在")
    # 删除公司的所有部门（会级联删除团队与成员）
    depts = (await db.execute(
        select(BizDepartment).where(BizDepartment.company_id == c.id)
    )).scalars().all()
    for d in depts:
        teams = (await db.execute(
            select(BizTeam).where(BizTeam.department_id == d.id)
        )).scalars().all()
        for t in teams:
            await db.execute(delete(BizTeamMember).where(BizTeamMember.team_id == t.id))
        await db.execute(delete(BizTeam).where(BizTeam.department_id == d.id))
    await db.execute(delete(BizDepartment).where(BizDepartment.company_id == c.id))
    await db.delete(c)
    await db.commit()
    return Response.ok({"deleted": company_id})


# ── 部门 ──

@router.get("/departments")
async def list_departments(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """获取所有部门。"""
    rows = (await db.execute(select(BizDepartment))).scalars().all()
    return Response.ok([d.to_dict() for d in rows])


@router.post("/departments")
async def create_department(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """创建部门。"""
    name = body.get("name")
    code = body.get("code")
    company_id = body.get("company_id")
    if not name or not code or not company_id:
        raise HTTPException(status_code=400, detail="name/code/company_id 必填")
    company = await db.get(SysCompany, int(company_id))
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    exists = (await db.execute(
        select(BizDepartment).where(BizDepartment.code == code)
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=f"部门编码 {code} 已存在")
    d = BizDepartment(
        name=name, code=code,
        company_id=int(company_id),
        parent_id=body.get("parent_id") or None,
        created_by=current_user.id,
    )
    db.add(d)
    await db.commit()
    await db.refresh(d)
    return Response.ok(d.to_dict())


@router.put("/departments/{dept_id}")
async def update_department(
    dept_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """更新部门。"""
    d = await db.get(BizDepartment, dept_id)
    if not d:
        raise HTTPException(status_code=404, detail="部门不存在")
    if "name" in body and body["name"]:
        d.name = body["name"]
    if "code" in body and body["code"]:
        d.code = body["code"]
    await db.commit()
    return Response.ok(d.to_dict())


@router.delete("/departments/{dept_id}")
async def delete_department(
    dept_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """删除部门（级联删除团队与成员）。"""
    d = await db.get(BizDepartment, dept_id)
    if not d:
        raise HTTPException(status_code=404, detail="部门不存在")
    teams = (await db.execute(
        select(BizTeam).where(BizTeam.department_id == d.id)
    )).scalars().all()
    for t in teams:
        await db.execute(delete(BizTeamMember).where(BizTeamMember.team_id == t.id))
    await db.execute(delete(BizTeam).where(BizTeam.department_id == d.id))
    await db.delete(d)
    await db.commit()
    return Response.ok({"deleted": dept_id})


# ── 团队 ──

@router.get("/teams")
async def list_teams(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """获取所有团队。"""
    rows = (await db.execute(select(BizTeam))).scalars().all()
    return Response.ok([t.to_dict() for t in rows])


@router.post("/teams")
async def create_team(
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """创建团队。"""
    name = body.get("name")
    code = body.get("code")
    department_id = body.get("department_id")
    if not name or not code or not department_id:
        raise HTTPException(status_code=400, detail="name/code/department_id 必填")
    dept = await db.get(BizDepartment, int(department_id))
    if not dept:
        raise HTTPException(status_code=404, detail="部门不存在")
    exists = (await db.execute(
        select(BizTeam).where(BizTeam.code == code)
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail=f"团队编码 {code} 已存在")
    t = BizTeam(
        name=name, code=code,
        department_id=int(department_id),
        description=body.get("description"),
        created_by=current_user.id,
    )
    db.add(t)
    await db.commit()
    await db.refresh(t)
    return Response.ok(t.to_dict())


@router.put("/teams/{team_id}")
async def update_team(
    team_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """更新团队。"""
    t = await db.get(BizTeam, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="团队不存在")
    if "name" in body and body["name"]:
        t.name = body["name"]
    if "code" in body and body["code"]:
        t.code = body["code"]
    if "description" in body:
        t.description = body["description"]
    await db.commit()
    return Response.ok(t.to_dict())


@router.delete("/teams/{team_id}")
async def delete_team(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """删除团队。"""
    t = await db.get(BizTeam, team_id)
    if not t:
        raise HTTPException(status_code=404, detail="团队不存在")
    await db.execute(delete(BizTeamMember).where(BizTeamMember.team_id == t.id))
    await db.delete(t)
    await db.commit()
    return Response.ok({"deleted": team_id})


# ── 团队成员（人员权限维护） ──

@router.get("/teams/{team_id}/members")
async def list_team_members(
    team_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """获取团队成员列表（含用户信息）。"""
    rows = (await db.execute(
        select(SysUser, BizTeamMember)
        .join(BizTeamMember, BizTeamMember.user_id == SysUser.id)
        .where(BizTeamMember.team_id == team_id)
    )).all()
    return Response.ok([{
        "user_id": str(u.id),
        "username": u.username,
        "nickname": u.nickname,
        "email": u.email,
        "status": u.status.value,
        "team_role": m.role,
    } for u, m in rows])


@router.post("/teams/{team_id}/members")
async def add_team_member(
    team_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """添加团队成员。"""
    user_id = body.get("user_id")
    role = body.get("role", "member")
    if not user_id:
        raise HTTPException(status_code=400, detail="user_id 必填")
    team = await db.get(BizTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="团队不存在")
    user = await db.get(SysUser, int(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    exists = (await db.execute(
        select(BizTeamMember).where(
            BizTeamMember.team_id == team_id,
            BizTeamMember.user_id == int(user_id),
        )
    )).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=409, detail="用户已是团队成员")
    m = BizTeamMember(team_id=team_id, user_id=int(user_id), role=role)
    db.add(m)
    await db.commit()
    await db.refresh(m)
    return Response.ok(m.to_dict())


@router.put("/teams/{team_id}/members/{user_id}")
async def update_team_member(
    team_id: int,
    user_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """更新团队成员角色（admin / member）。"""
    m = (await db.execute(
        select(BizTeamMember).where(
            BizTeamMember.team_id == team_id,
            BizTeamMember.user_id == user_id,
        )
    )).scalar_one_or_none()
    if not m:
        raise HTTPException(status_code=404, detail="成员不存在")
    if "role" in body and body["role"] in ("admin", "member", "viewer"):
        m.role = body["role"]
    await db.commit()
    return Response.ok(m.to_dict())


@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """移除团队成员。"""
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


# ── 树形结构（前端展示） ──

@router.get("/tree")
async def get_org_tree(
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """获取完整组织树（公司→部门→团队→成员）。"""
    companies = (await db.execute(select(SysCompany))).scalars().all()
    tree = []
    for c in companies:
        depts = (await db.execute(
            select(BizDepartment).where(BizDepartment.company_id == c.id)
        )).scalars().all()
        dept_nodes = []
        for d in depts:
            teams = (await db.execute(
                select(BizTeam).where(BizTeam.department_id == d.id)
            )).scalars().all()
            team_nodes = []
            for t in teams:
                members = (await db.execute(
                    select(SysUser, BizTeamMember)
                    .join(BizTeamMember, BizTeamMember.user_id == SysUser.id)
                    .where(BizTeamMember.team_id == t.id)
                )).all()
                team_nodes.append({
                    "id": str(t.id),
                    "name": t.name,
                    "code": t.code,
                    "type": "team",
                    "description": t.description,
                    "members": [{
                        "user_id": str(u.id),
                        "username": u.username,
                        "nickname": u.nickname,
                        "team_role": m.role,
                    } for u, m in members],
                })
            dept_nodes.append({
                "id": str(d.id),
                "name": d.name,
                "code": d.code,
                "type": "department",
                "parent_id": str(d.parent_id) if d.parent_id else None,
                "children": team_nodes,
            })
        tree.append({
            "id": str(c.id),
            "name": c.name,
            "code": c.code,
            "type": "company",
            "children": dept_nodes,
        })
    return Response.ok(tree)


# ── 上传组织结构 ──

@router.post("/upload")
async def upload_org_structure(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: SysUser = Depends(get_current_user),
):
    """上传组织结构（JSON 格式）。
    JSON 示例:
    {
      "companies": [
        {"name": "示例公司", "code": "DEMO",
         "departments": [
           {"name": "研发部", "code": "RD",
            "teams": [{"name": "前端组", "code": "FE"}]
           }
         ]
        }
      ]
    }
    """
    import json as _json
    content = await file.read()
    try:
        data = _json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"JSON 解析失败: {e}")

    companies = data.get("companies", [])
    created = {"companies": 0, "departments": 0, "teams": 0}

    for c in companies:
        cname = c.get("name")
        ccode = c.get("code")
        if not cname or not ccode:
            continue
        exists = (await db.execute(
            select(SysCompany).where(SysCompany.code == ccode)
        )).scalar_one_or_none()
        if not exists:
            company = SysCompany(name=cname, code=ccode)
            db.add(company)
            await db.flush()
            created["companies"] += 1
        else:
            company = exists
        for d in c.get("departments", []):
            dname = d.get("name")
            dcode = d.get("code")
            if not dname or not dcode:
                continue
            dexists = (await db.execute(
                select(BizDepartment).where(BizDepartment.code == dcode)
            )).scalar_one_or_none()
            if not dexists:
                dept = BizDepartment(
                    name=dname, code=dcode,
                    company_id=company.id, created_by=current_user.id,
                )
                db.add(dept)
                await db.flush()
                created["departments"] += 1
            else:
                dept = dexists
            for t in d.get("teams", []):
                tname = t.get("name")
                tcode = t.get("code")
                if not tname or not tcode:
                    continue
                texists = (await db.execute(
                    select(BizTeam).where(BizTeam.code == tcode)
                )).scalar_one_or_none()
                if not texists:
                    team = BizTeam(
                        name=tname, code=tcode,
                        department_id=dept.id,
                        description=t.get("description"),
                        created_by=current_user.id,
                    )
                    db.add(team)
                    await db.flush()
                    created["teams"] += 1
    await db.commit()
    return Response.ok({"message": "组织结构上传完成", "created": created})
