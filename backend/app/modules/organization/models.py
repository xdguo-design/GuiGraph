"""组织架构模块 ORM 模型。"""

from sqlalchemy import String, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database.base import Base, TimestampMixin


class SysCompany(Base, TimestampMixin):
    """公司表。"""
    __tablename__ = "sys_company"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="公司名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="公司编码")

    departments = relationship("BizDepartment", back_populates="company")

    def to_dict(self) -> dict:
        return {"id": str(self.id), "name": self.name, "code": self.code}


class BizDepartment(Base, TimestampMixin):
    """部门表。"""
    __tablename__ = "biz_department"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="部门名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="部门编码")
    company_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属公司 ID")
    parent_id: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="父部门 ID")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    company = relationship("SysCompany", back_populates="departments")
    teams = relationship("BizTeam", back_populates="department", cascade="all, delete-orphan")
    sub_departments = relationship("BizDepartment", back_populates="parent_department")
    parent_department = relationship("BizDepartment", remote_side=[id], back_populates="sub_departments")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "company_id": str(self.company_id),
            "parent_id": str(self.parent_id) if self.parent_id else None,
            "created_by": str(self.created_by),
        }


class BizTeam(Base, TimestampMixin):
    """团队表。"""
    __tablename__ = "biz_team"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="团队名称")
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment="团队编码")
    department_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="所属部门 ID")
    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="团队描述")
    created_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="创建人 ID")

    department = relationship("BizDepartment", back_populates="teams")
    members = relationship("BizTeamMember", back_populates="team", cascade="all, delete-orphan")
    git_repos = relationship("BizGitRepo", back_populates="team", cascade="all, delete-orphan")
    domains = relationship("BizDomain", back_populates="team", cascade="all, delete-orphan")
    applications = relationship("BizApplication", back_populates="team", cascade="all, delete-orphan")
    components = relationship("BizComponent", back_populates="team", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "name": self.name,
            "code": self.code,
            "department_id": str(self.department_id),
            "description": self.description,
            "created_by": str(self.created_by),
        }


class BizTeamMember(Base, TimestampMixin):
    """团队成员表。"""
    __tablename__ = "biz_team_member"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    team_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="团队 ID")
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="用户 ID")
    role: Mapped[str] = mapped_column(String(20), default="member", comment="团队内角色: admin/member")

    team = relationship("BizTeam", back_populates="members")

    __table_args__ = ({"UniqueConstraint": ("team_id", "user_id", name="uk_team_user")},)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "team_id": str(self.team_id),
            "user_id": str(self.user_id),
            "role": self.role,
        }
