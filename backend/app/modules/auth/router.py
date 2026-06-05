"""认证模块路由。"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security.jwt import create_access_token, create_refresh_token, verify_token
from app.core.security.wechat import wechat_client
from app.core.utils.response import Response
from app.modules.auth.schemas import LoginRequest, TokenResponse, WechatQRCodeResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest):
    """用户名密码登录（MD5 加密）。"""
    from app.modules.auth.service import auth_service

    user = await auth_service.authenticate_user(body.username, body.password)
    if not user:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token({"sub": user["id"], "username": user["username"], "role": user.get("role", "editor")})
    refresh_token = create_refresh_token({"sub": user["id"], "username": user["username"], "role": user.get("role", "editor")})

    return Response.ok(TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=7200,
    ))


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
    # TODO: 加入令牌黑名单
    return Response.ok({"message": "退出成功"})
