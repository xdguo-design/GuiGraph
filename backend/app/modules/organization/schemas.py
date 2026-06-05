"""组织架构模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field


class CompanyCreate(BaseModel):
    """创建公司。"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)


class CompanyResponse(BaseModel):
    """公司响应。"""
    id: str
    name: str
    code: str


class DepartmentCreate(BaseModel):
    """创建部门。"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    company_id: str
    parent_id: Optional[str] = None


class DepartmentResponse(BaseModel):
    """部门响应。"""
    id: str
    name: str
    code: str
    company_id: str
    parent_id: Optional[str]
    created_by: str


class TeamCreate(BaseModel):
    """创建团队。"""
    name: str = Field(..., min_length=1, max_length=100)
    code: str = Field(..., min_length=1, max_length=50)
    department_id: str
    description: Optional[str] = None


class TeamResponse(BaseModel):
    """团队响应。"""
    id: str
    name: str
    code: str
    department_id: str
    description: Optional[str]
    created_by: str


class TeamMemberAdd(BaseModel):
    """添加团队成员。"""
    user_id: str
    role: str = Field("member", description="团队内角色: admin/member")


class OrgStructureResponse(BaseModel):
    """组织架构树响应。"""
    companies: list[dict]
    message: str = "success"
