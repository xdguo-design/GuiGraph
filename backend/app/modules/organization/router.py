"""组织架构模块路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user, check_role
from app.core.utils.response import Response
from app.modules.organization.schemas import (
    CompanyCreate, CompanyResponse,
    DepartmentCreate, DepartmentResponse,
    TeamCreate, TeamResponse, TeamMemberAdd,
    OrgStructureResponse,
)

router = APIRouter()


@router.get("/structure", response_model=OrgStructureResponse)
async def get_structure(user_id: str = Depends(get_current_user)):
    """获取完整组织架构树。"""
    # TODO: 从数据库查询
    return Response.ok(OrgStructureResponse(
        companies=[],
        message="获取成功",
    ))


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    body: DepartmentCreate,
    user_id: str = Depends(get_current_user),
):
    """创建部门。"""
    # TODO: 创建部门
    return Response.ok(DepartmentResponse(
        id="dept_001",
        name=body.name,
        code=body.code,
        company_id=body.company_id,
        parent_id=body.parent_id,
        created_by=user_id,
    ))


@router.put("/departments/{dept_id}")
async def update_department(
    dept_id: str,
    body: DepartmentCreate,
    user_id: str = Depends(get_current_user),
):
    """更新部门。"""
    return Response.ok({"message": "更新成功"})


@router.post("/teams", response_model=TeamResponse)
async def create_team(
    body: TeamCreate,
    user_id: str = Depends(get_current_user),
):
    """创建团队。"""
    return Response.ok(TeamResponse(
        id="team_001",
        name=body.name,
        code=body.code,
        department_id=body.department_id,
        description=body.description,
        created_by=user_id,
    ))


@router.put("/teams/{team_id}")
async def update_team(
    team_id: str,
    body: TeamCreate,
    user_id: str = Depends(get_current_user),
):
    """更新团队。"""
    return Response.ok({"message": "更新成功"})


@router.post("/teams/{team_id}/members")
async def add_team_member(
    team_id: str,
    body: TeamMemberAdd,
    user_id: str = Depends(get_current_user),
):
    """添加团队成员。"""
    return Response.ok({"message": "添加成功"})


@router.delete("/teams/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: str,
    user_id: str,
    current_user: str = Depends(get_current_user),
):
    """移除团队成员。"""
    return Response.ok({"message": "移除成功"})
