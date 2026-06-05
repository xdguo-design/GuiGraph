"""用户模块路由。"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.modules.user.schemas import UserProfile, AvatarUploadResponse, BindWechatRequest

router = APIRouter()


@router.get("/profile", response_model=UserProfile)
async def get_profile(user_id: str = Depends(get_current_user)):
    """获取当前用户信息。"""
    # TODO: 从数据库查询
    return Response.ok(UserProfile(
        id=user_id,
        username="test_user",
        nickname="测试用户",
        avatar_url="",
        email="test@example.com",
        phone="",
        status="active",
        roles=["editor"],
    ))


@router.put("/profile")
async def update_profile(
    body: UserProfile,
    user_id: str = Depends(get_current_user),
):
    """更新用户信息。"""
    # TODO: 更新数据库
    return Response.ok({"message": "更新成功"})


@router.post("/avatar", response_model=AvatarUploadResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user),
):
    """上传头像。"""
    # TODO: 上传至 MinIO
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="仅支持图片文件",
        )
    return Response.ok(AvatarUploadResponse(
        avatar_url=f"/api/v1/user/avatar/{user_id}/avatar.jpg",
        message="上传成功",
    ))


@router.post("/bind-wechat")
async def bind_wechat(
    body: BindWechatRequest,
    user_id: str = Depends(get_current_user),
):
    """绑定微信账号。"""
    # TODO: 验证微信 code 并绑定
    return Response.ok({"message": "绑定成功"})
