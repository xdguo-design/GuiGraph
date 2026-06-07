"""附件模块路由。"""
import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.deps.auth import get_current_user
from app.core.database.session import get_db
from app.core.utils.response import Response
from app.modules.attachment.schemas import FileUploadResponse, FileInfo
from app.modules.attachment.models import BizAttachFile
from app.shared.enums import BizFileType, FileAttachmentType

router = APIRouter()

# 上传目录：项目根 backend/uploads/attachments
BACKEND_DIR = Path(__file__).resolve().parents[3]
UPLOAD_DIR = BACKEND_DIR / "uploads" / "attachments"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def _public_base_url() -> str:
    """前端通过 Vite 代理 /uploads 访问此路径。"""
    return "/uploads/attachments"


# 允许的图片类型
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}
# 允许的文档类型
ALLOWED_DOC_TYPES = {
    "application/pdf": ".pdf",
    "application/zip": ".zip",
    "application/x-rar-compressed": ".rar",
    "application/msword": ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.ms-excel": ".xls",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "text/plain": ".txt",
    "text/markdown": ".md",
}
ALLOWED_TYPES = {**ALLOWED_IMAGE_TYPES, **ALLOWED_DOC_TYPES}
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB


def _infer_file_type(content_type: str) -> FileAttachmentType:
    if content_type.startswith("image/"):
        return FileAttachmentType.IMAGE
    return FileAttachmentType.DOCUMENT


@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    biz_type: str = "change",
    biz_id: str = "0",
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """上传文件：保存到本地 uploads/attachments/，写入 biz_attach_file 表。"""
    if not file.content_type or file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的文件类型: {file.content_type}。仅支持图片/PDF/Office/压缩包",
        )

    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件为空",
        )
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件过大（{len(content) // 1024 // 1024}MB），最大 {MAX_FILE_SIZE // 1024 // 1024}MB",
        )

    ext = ALLOWED_TYPES[file.content_type]
    stored_name = f"{biz_type}_{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / stored_name
    with open(save_path, "wb") as f:
        f.write(content)

    # 落库（可选，做记录以便后续按 biz 查询附件）
    try:
        biz_type_enum = BizFileType(biz_type) if biz_type in {e.value for e in BizFileType} else BizFileType.CHANGE
        record = BizAttachFile(
            biz_type=biz_type_enum,
            biz_id=int(biz_id) if str(biz_id).isdigit() else 0,
            file_type=_infer_file_type(file.content_type),
            minio_bucket="local",
            minio_path=stored_name,
            file_size=len(content),
            upload_time=datetime.utcnow(),
            uploaded_by=current_user.id,
        )
        db.add(record)
        await db.commit()
        await db.refresh(record)
        file_id = str(record.id)
    except Exception:
        # 落库失败不影响文件本身可用
        file_id = stored_name

    file_url = f"{_public_base_url()}/{stored_name}"
    return Response.ok(FileUploadResponse(
        file_id=file_id,
        file_url=file_url,
        file_name=file.filename or stored_name,
        file_size=len(content),
        biz_type=biz_type,
        biz_id=biz_id,
    ))


@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """删除附件：从磁盘 + DB 一同删除。"""
    deleted = False
    # 数字 id → DB 查
    if file_id.isdigit():
        result = await db.execute(
            select(BizAttachFile).where(BizAttachFile.id == int(file_id))
        )
        record = result.scalar_one_or_none()
        if record:
            try:
                (UPLOAD_DIR / record.minio_path).unlink(missing_ok=True)
            except OSError:
                pass
            await db.delete(record)
            await db.commit()
            deleted = True
    if not deleted:
        # 按文件名直接删（兼容未落库的旧数据）
        target = UPLOAD_DIR / file_id
        if target.exists() and target.is_file():
            try:
                target.unlink()
                deleted = True
            except OSError:
                pass
    return Response.ok({"deleted": deleted})


@router.get("/download/{file_id}")
async def download_file(file_id: str, user_id: str = Depends(get_current_user)):
    """下载文件（占位）。"""
    return Response.ok({"message": "下载中"})


@router.get("/list")
async def list_files(
    biz_type: str = "",
    biz_id: str = "",
    user_id: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """列出附件。"""
    query = select(BizAttachFile)
    if biz_type:
        try:
            query = query.where(BizAttachFile.biz_type == BizFileType(biz_type))
        except ValueError:
            pass
    if biz_id and biz_id.isdigit():
        query = query.where(BizAttachFile.biz_id == int(biz_id))
    rows = (await db.execute(query)).scalars().all()
    return Response.ok({
        "items": [
            {
                **r.to_dict(),
                "file_url": f"{_public_base_url()}/{r.minio_path}",
            }
            for r in rows
        ]
    })
