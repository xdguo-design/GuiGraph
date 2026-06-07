"""认证模块路由。"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.deps.auth import get_current_user, check_role
from app.core.security.jwt import create_access_token, create_refresh_token, verify_token
from app.core.security.wechat import wechat_client
from app.core.utils.response import Response
from app.modules.auth.schemas import LoginRequest, TokenResponse, WechatQRCodeResponse
from app.modules.user.models import SysUser
from app.modules.user.schemas import ApplicationSubmit, ApplicationReview, ApplicationReject

router = APIRouter()


@router.post("/login")
async def login(body: LoginRequest):
    """用户名密码登录（MD5 加密）。仅 ACTIVE 状态的用户可登录。"""
    from app.modules.auth.service import auth_service

    user = await auth_service.authenticate_user(body.username, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误，或账号未激活",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user["id"], "username": user["username"], "role": user.get("role", "editor")})
    refresh_token = create_refresh_token({"sub": user["id"], "username": user["username"], "role": user.get("role", "editor")})

    return Response.ok({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": 7200,
    })


@router.post("/wechat/qrcode", response_model=WechatQRCodeResponse)
async def get_wechat_qrcode():
    """获取微信登录二维码。"""
    url = await wechat_client.get_qrconnect_url("http://localhost:8000/api/v1/auth/wechat/callback")
    if not url:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="微信登录未配置",
        )
    return Response.ok(WechatQRCodeResponse(qr_url=url))


@router.get("/wechat/callback")
async def wechat_callback(code: str, state: str = ""):
    """微信授权回调。"""
    user_info = await wechat_client.get_user_info(code)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信授权失败",
        )
    # TODO: 根据 openid 查找/创建用户，生成 token
    return Response.ok({"user_info": user_info})


@router.post("/refresh")
async def refresh_token(refresh_token: str):
    """刷新访问令牌。"""
    payload = verify_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
        )
    new_access = create_access_token({"sub": payload.get("sub"), "username": payload.get("username")})
    new_refresh = create_refresh_token({"sub": payload.get("sub"), "username": payload.get("username")})
    return Response.ok({"access_token": new_access, "refresh_token": new_refresh})


@router.post("/logout")
async def logout():
    """退出登录。"""
    return Response.ok({"message": "退出成功"})


# ── 注册申请（公开） ──

@router.post("/apply")
async def submit_application(body: ApplicationSubmit):
    """提交注册申请（公开接口）。"""
    from app.modules.auth.service import auth_service

    try:
        result = await auth_service.submit_application(
            username=body.username,
            password=body.password,
            nickname=body.nickname or "",
            email=body.email or "",
            phone=body.phone or "",
            reason=body.reason or "",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return Response.ok({
        "id": result["id"],
        "message": "申请已提交，请等待管理员审核",
    })


# ── 注册申请管理（管理员） ──

@router.get("/applications")
async def list_applications(
    status_filter: str | None = None,
    current_user: SysUser = Depends(get_current_user),
):
    """列出注册申请（管理员）。"""
    # 真正的管理员：role 为 system_admin / dept_admin / team_admin，或内置账号
    admin_roles = {"system_admin", "dept_admin", "team_admin"}
    if current_user.username not in ("admin", "guoxudong"):
        # 需要再查一次 token 中的 role（current_user 本身不带 role 字段）
        from app.core.security.jwt import verify_token
        from app.core.deps.auth import security
        # 简单办法：直接查 application 中最近一次被分配的角色
        from app.modules.auth.service import auth_service
        from app.modules.user.models import SysUserApplication
        from app.shared.enums import ApplicationStatus
        from app.core.database.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            # 这里仅以 username+APPROVED 最新一条作为判据
            from sqlalchemy import select
            app = (await session.execute(
                select(SysUserApplication)
                .where(
                    SysUserApplication.username == current_user.username,
                    SysUserApplication.status == ApplicationStatus.APPROVED,
                )
                .order_by(SysUserApplication.reviewed_at.desc())
                .limit(1)
            )).scalar_one_or_none()
            assigned = app.assigned_role if app else None
        if assigned not in admin_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="权限不足")

    from app.modules.auth.service import auth_service
    apps = await auth_service.list_applications(status_filter=status_filter)
    return Response.ok({"list": apps, "total": len(apps)})


@router.post("/applications/{application_id}/approve")
async def approve_application(
    application_id: int,
    body: ApplicationReview,
    current_user: SysUser = Depends(get_current_user),
):
    """审核通过：创建用户并分配角色/组织（管理员）。"""
    from app.modules.auth.service import auth_service
    try:
        result = await auth_service.approve_application(
            application_id=application_id,
            reviewer_id=current_user.id,
            role=body.role,
            company_id=body.company_id or "",
            department_id=body.department_id or "",
            team_id=body.team_id or "",
            comment=body.comment or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response.ok(result)


@router.post("/applications/{application_id}/reject")
async def reject_application(
    application_id: int,
    body: ApplicationReject,
    current_user: SysUser = Depends(get_current_user),
):
    """审核拒绝（管理员）。"""
    from app.modules.auth.service import auth_service
    try:
        result = await auth_service.reject_application(
            application_id=application_id,
            reviewer_id=current_user.id,
            comment=body.comment or "",
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return Response.ok(result)
