"""看板模块 Schema 定义。"""

from typing import Optional

from pydantic import BaseModel, Field


class GanttTask(BaseModel):
    """Gantt 图任务项。"""
    id: str = Field(..., description="变更 ID")
    content: str = Field(..., description="变更内容")
    start_date: str = Field(..., description="开始日期 YYYY-MM-DD")
    end_date: str = Field(..., description="结束日期 YYYY-MM-DD")
    team_id: Optional[str] = Field(None, description="团队 ID")
    team_name: Optional[str] = Field(None, description="团队名称")
    team_color: Optional[str] = Field(None, description="团队颜色")
    change_type: str = Field(..., description="变更类型")
    status: str = Field(..., description="变更状态")


class GanttDependency(BaseModel):
    """Gantt 图依赖关系。"""
    id: str = Field(..., description="依赖关系 ID")
    from_id: str = Field(..., description="前置任务 ID")
    to_id: str = Field(..., description="后置任务 ID")
    type: str = Field(..., description="依赖类型 (FS)")


class GanttResponse(BaseModel):
    """Gantt 图响应。"""
    tasks: list[GanttTask] = Field(default_factory=list, description="任务列表")
    dependencies: list[GanttDependency] = Field(default_factory=list, description="依赖关系列表")
