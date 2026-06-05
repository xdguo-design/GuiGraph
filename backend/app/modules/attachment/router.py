"""附件模块路由。"""

from fastapi import APIRouter, Depends, UploadFile, File

from app.core.deps.auth import get_current_user
from app.core.utils.response import Response
from app.modules.attachment.schemas import FileUploadResponse, FileInfo

router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    biz_type: str = "change",
    biz_id: str = "",
    user_id: str = Depends(get_current_user),
):
    """上传文件至 MinIO。"""
    # TODO: 实际上传至 MinIO
    return Response.ok(FileUploadResponse(
        file_id="file_001",
        file_url=f"/api/v1/attachment/download/file_001",
        file_name=file.filename,
        file_size=0,
        biz_type=biz_type,
        biz_id=biz_id,
    ))


@router.get("/download/{file_id}")
async def download_file(file_id: str, user_id: str = Depends(get_current_user)):
    """下载文件。"""
    # TODO: 从 MinIO 下载
    return Response.ok({"message": "下载中"})


@router.delete("/delete/{file_id}")
async def delete_file(file_id: str, user_id: str = Depends(get_current_user)):
    """删除文件。"""
    return Response.ok({"message": "删除成功"})


@router.get("/list")
async def list_files(
    biz_type: str = "",
    biz_id: str = "",
    user_id: str = Depends(get_current_user),
):
    """列出附件。"""
    return Response.ok({"items": []})
