"""Jenkins 集成模块路由。"""

from fastapi import APIRouter, Depends

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.modules.jenkins.schemas import (
    JenkinsInstanceCreate, JenkinsInstanceResponse,
    BuildRequest, BuildStatusResponse, BuildLogResponse,
)

router = APIRouter()


@router.get("/instances")
async def list_instances(user_id: str = Depends(get_current_user)):
    """获取 Jenkins 实例列表。"""
    return Response.ok({"items": []})


@router.post("/instances", response_model=JenkinsInstanceResponse)
async def create_instance(
    body: JenkinsInstanceCreate,
    user_id: str = Depends(get_current_user),
):
    """添加 Jenkins 实例。"""
    return Response.ok(JenkinsInstanceResponse(
        id="jenkins_001",
        name=body.name,
        url=body.url,
        auth_type=body.auth_type,
        created_by=user_id,
    ))


@router.post("/build", response_model=BuildStatusResponse)
async def trigger_build(
    body: BuildRequest,
    user_id: str = Depends(get_current_user),
):
    """触发构建。"""
    return Response.ok(BuildStatusResponse(
        build_id="build_001",
        job_name=body.job_name,
        status="running",
        message="构建已触发",
    ))


@router.get("/build/{build_id}/status", response_model=BuildStatusResponse)
async def get_build_status(build_id: str, user_id: str = Depends(get_current_user)):
    """获取构建状态。"""
    return Response.ok(BuildStatusResponse(
        build_id=build_id,
        job_name="sample-job",
        status="success",
        message="构建成功",
    ))


@router.get("/build/{build_id}/log", response_model=BuildLogResponse)
async def get_build_log(build_id: str, user_id: str = Depends(get_current_user)):
    """获取构建日志。"""
    return Response.ok(BuildLogResponse(
        build_id=build_id,
        log="[2026-06-04 14:00:00] Starting build...\n[2026-06-04 14:05:00] Build completed successfully.",
    ))


@router.post("/build/{build_id}/stop")
async def stop_build(build_id: str, user_id: str = Depends(get_current_user)):
    """停止构建。"""
    return Response.ok({"message": "停止请求已发送"})


@router.post("/changes/{change_id}/jenkins-status")
async def update_change_jenkins_status(
    change_id: str,
    build_id: str,
    status: str,
    user_id: str = Depends(get_current_user),
):
    """回写 Jenkins 状态至变更条目。"""
    return Response.ok({"message": "状态更新成功"})
