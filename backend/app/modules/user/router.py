"""用户模块路由。"""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.settings import settings
from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.integrations.wechat import wechat_client
from app.modules.user.schemas import (
    UserProfile,
    UserProfileUpdate,
    AvatarUploadResponse,
    BindWechatRequest,
    BindWechatResponse,
    WechatQrCodeResponse,
)
from app.modules.user.models import SysUser

router = APIRouter()

# 上传目录（项目根下 backend/uploads/avatars）
BACKEND_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BACKEND_DIR / "uploads" / "avatars"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _public_base_url() -> str:
    """构造公开访问 URL（前端通过 Vite 代理 /uploads 到后端）。"""
    return "/uploads/avatars"


@router.get("/profile")
async def get_profile(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """获取当前用户信息。"""
    result = await db.execute(
        select(SysUser).where(SysUser.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return Response.error("用户不存在", code="USER_NOT_FOUND")

    avatar_url = user.avatar_url or ""
    # 如果是相对路径，补全为可访问 URL
    if avatar_url and not avatar_url.startswith(("http://", "https://", "/")):
        avatar_url = f"{_public_base_url()}/{avatar_url}"
    # 没有头像时返回默认头像
    elif not avatar_url:
        avatar_url = f"{_public_base_url()}/default-avatar.svg"

    return Response.ok(
        {
            "id": str(user.id),
            "username": user.username,
            "nickname": user.nickname or "",
            "avatar_url": avatar_url,
            "email": user.email or "",
            "phone": user.phone or "",
            "status": user.status.value,
            "wechat_bound": bool(user.wechat_openid),
            "wechat_openid": user.wechat_openid or "",
        }
    )


@router.put("/profile")
async def update_profile(
    body: UserProfileUpdate,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """更新用户信息。"""
    result = await db.execute(
        select(SysUser).where(SysUser.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        return Response.error("用户不存在", code="USER_NOT_FOUND")

    if body.nickname is not None:
        user.nickname = body.nickname
    if body.email is not None:
        user.email = body.email
    if body.phone is not None:
        user.phone = body.phone

    await db.commit()
    await db.refresh(user)

    return Response.ok(
        {
            "id": str(user.id),
            "username": user.username,
            "nickname": user.nickname,
            "email": user.email,
            "phone": user.phone,
            "avatar_url": user.avatar_url or "",
        }
    )


# 允许的图片类型与扩展名映射
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
}
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2MB


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传头像：保存到本地 uploads/avatars/，并写入用户 avatar_url。"""
    if not file.content_type or file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的图片类型: {file.content_type}。仅支持 {', '.join(ALLOWED_IMAGE_TYPES.keys())}",
        )

    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"头像文件过大（{len(content) // 1024}KB），最大 {MAX_AVATAR_SIZE // 1024 // 1024}MB",
        )
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="头像文件为空",
        )

    ext = ALLOWED_IMAGE_TYPES[file.content_type]
    filename = f"user_{current_user.id}_{uuid.uuid4().hex[:8]}{ext}"
    save_path = UPLOAD_DIR / filename

    with open(save_path, "wb") as f:
        f.write(content)

    # 删除旧头像
    if current_user.avatar_url:
        old_name = Path(current_user.avatar_url).name
        old_path = UPLOAD_DIR / old_name
        if old_path.exists() and old_path != save_path:
            try:
                old_path.unlink()
            except OSError:
                pass

    # 写库
    user_result = await db.execute(
        select(SysUser).where(SysUser.id == current_user.id)
    )
    user = user_result.scalar_one_or_none()
    if user:
        user.avatar_url = filename
        user.updated_at = datetime.utcnow()
        await db.commit()

    avatar_url = f"{_public_base_url()}/{filename}"
    return Response.ok(AvatarUploadResponse(
        avatar_url=avatar_url,
        message="头像上传成功",
    ))


@router.post("/bind-wechat")
async def bind_wechat(
    body: BindWechatRequest,
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """绑定微信账号：未配置微信 AppId 时走开发模式（生成 mock openid）。"""
    if not body.code or len(body.code) < 4:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的微信授权码",
        )

    # 1) 真实模式（有 app id/secret）：通过微信 API 换 openid
    if settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET:
        wx_info = await wechat_client.get_user_info(body.code)
        openid = wx_info.get("openid")
        unionid = wx_info.get("unionid")
        nickname = wx_info.get("nickname")
        if not openid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"微信授权失败：{wx_info}",
            )
    else:
        # 2) 开发模式：使用 code 派生一个稳定的 mock openid
        #    避免每次绑定都不同，方便测试
        import hashlib
        digest = hashlib.md5(f"mock-wechat-{body.code}".encode()).hexdigest()
        openid = f"mock_openid_{digest[:24]}"
        unionid = f"mock_unionid_{digest[:24]}"
        nickname = f"微信用户_{body.code[-4:]}"

    # 3) 写库
    user_result = await db.execute(
        select(SysUser).where(SysUser.id == current_user.id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )

    # 检查 openid 是否已被其他用户占用
    dup_result = await db.execute(
        select(SysUser).where(
            SysUser.wechat_openid == openid,
            SysUser.id != current_user.id,
        )
    )
    if dup_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="该微信账号已绑定其他用户",
        )

    user.wechat_openid = openid
    user.wechat_unionid = unionid
    user.updated_at = datetime.utcnow()
    # 如果用户没有昵称，使用微信昵称
    if not user.nickname and nickname:
        user.nickname = nickname
    await db.commit()

    return Response.ok(BindWechatResponse(
        openid=openid,
        nickname=nickname or "",
        message="微信绑定成功",
        mode="real" if (settings.WECHAT_APP_ID and settings.WECHAT_APP_SECRET) else "mock",
    ))


@router.post("/unbind-wechat")
async def unbind_wechat(
    current_user: SysUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """解绑微信。"""
    user_result = await db.execute(
        select(SysUser).where(SysUser.id == current_user.id)
    )
    user = user_result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在",
        )
    user.wechat_openid = None
    user.wechat_unionid = None
    user.updated_at = datetime.utcnow()
    await db.commit()
    return Response.ok({"message": "解绑成功"})


@router.get("/wechat-qrcode")
async def get_wechat_qrcode(
    current_user: SysUser = Depends(get_current_user),
):
    """获取微信绑定二维码：未配置时返回 dev 模式提示。"""
    if not settings.WECHAT_APP_ID:
        # 开发模式：返回说明，前端展示一个提示框让用户输入 mock code
        return Response.ok(WechatQrCodeResponse(
            qr_url="",
            mode="dev",
            tip="开发模式：请直接使用任意 4 位以上字符串作为 code 提交即可模拟绑定",
        ))
    qr_url = await wechat_client.get_qrconnect_url(
        redirect_uri=settings.WECHAT_REDIRECT_URI,
        state=str(current_user.id),
    )
    return Response.ok(WechatQrCodeResponse(
        qr_url=qr_url,
        mode="real",
        tip="请使用微信扫描二维码完成绑定",
    ))
