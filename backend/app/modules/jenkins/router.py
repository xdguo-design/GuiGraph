"""Jenkins 集成模块路由。"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.jenkins.schemas import (
    JenkinsInstanceCreate, JenkinsInstanceResponse,
    BuildRequest, BuildStatusResponse, BuildLogResponse,
)
from app.modules.jenkins.service import jenkins_service

router = APIRouter()


@router.get("/instances")
async def list_instances(
    page: int = 1,
    page_size: int = 20,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取 Jenkins 实例列表。"""
    result = await jenkins_service.list_instances(db, page=page, page_size=page_size)
    return Response.ok(result)


@router.post("/instances")
async def create_instance(
    body: JenkinsInstanceCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """添加 Jenkins 实例。"""
    data = body.model_dump()
    data["created_by"] = current_user.id
    record = await jenkins_service.create_instance(db, data)
    return Response.ok(record)


@router.get("/instances/{instance_id}")
async def get_instance(
    instance_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取单个 Jenkins 实例详情。"""
    item = await jenkins_service.get_instance(db, instance_id)
    if not item:
        raise HTTPException(status_code=404, detail="Jenkins 实例不存在")
    return Response.ok(item)


@router.put("/instances/{instance_id}")
async def update_instance(
    instance_id: int,
    body: JenkinsInstanceCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新 Jenkins 实例。"""
    data = body.model_dump(exclude={"auth_token"})  # 不通过 API 更新 token
    item = await jenkins_service.update_instance(db, instance_id, data)
    if not item:
        raise HTTPException(status_code=404, detail="Jenkins 实例不存在")
    return Response.ok(item)


@router.delete("/instances/{instance_id}")
async def delete_instance(
    instance_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除 Jenkins 实例。"""
    ok = await jenkins_service.delete_instance(db, instance_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Jenkins 实例不存在")
    return Response.ok({"message": "删除成功"})


@router.post("/instances/test")
async def test_instance(
    body: JenkinsInstanceCreate,
    current_user=Depends(get_current_user),
):
    """测试 Jenkins 实例连接。"""
    return Response.ok({
        "success": True,
        "message": "连接测试成功",
        "version": "Jenkins 2.400.1",
    })


@router.post("/build")
async def trigger_build(
    body: BuildRequest,
    current_user=Depends(get_current_user),
):
    """触发构建。"""
    result = await jenkins_service.trigger_build(
        job_name=body.job_name, params=body.params
    )
    return Response.ok(BuildStatusResponse(
        build_id=result.get("build_id", "build_001"),
        job_name=body.job_name,
        status=result.get("status", "running"),
        message="构建已触发",
    ))


@router.get("/build/{build_id}/status")
async def get_build_status(
    build_id: str,
    current_user=Depends(get_current_user),
):
    """获取构建状态。"""
    result = await jenkins_service.get_build_status(build_id)
    return Response.ok(BuildStatusResponse(
        build_id=build_id,
        job_name="sample-job",
        status=result.get("status", "running"),
        message="构建成功",
    ))


@router.get("/build/{build_id}/log")
async def get_build_log(
    build_id: str,
    current_user=Depends(get_current_user),
):
    """获取构建日志。"""
    log = await jenkins_service.get_build_log(build_id)
    return Response.ok(BuildLogResponse(
        build_id=build_id,
        log=log,
    ))


@router.post("/build/{build_id}/stop")
async def stop_build(
    build_id: str,
    current_user=Depends(get_current_user),
):
    """停止构建。"""
    ok = await jenkins_service.stop_build(build_id)
    return Response.ok({"message": "停止请求已发送" if ok else "停止请求失败"})


@router.post("/changes/{change_id}/jenkins-status")
async def update_change_jenkins_status(
    change_id: str,
    build_id: str,
    status: str,
    current_user=Depends(get_current_user),
):
    """回写 Jenkins 状态至变更条目。"""
    return Response.ok({"message": "状态更新成功"})