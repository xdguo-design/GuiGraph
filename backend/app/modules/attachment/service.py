"""附件模块服务层。"""

from loguru import logger


class AttachmentService:
    """附件业务逻辑。"""

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        content_type: str,
        biz_type: str,
        biz_id: str,
        uploaded_by: str,
    ) -> str:
        """上传文件至 MinIO。"""
        logger.info(f"上传文件: {filename}, type={biz_type}, biz_id={biz_id}")
        return "file_001"

    async def get_file(self, file_id: str) -> dict | None:
        """获取文件信息。"""
        logger.info(f"查询文件: {file_id}")
        return None

    async def delete_file(self, file_id: str) -> bool:
        """删除文件。"""
        logger.info(f"删除文件: {file_id}")
        return True

    async def list_files(self, biz_type: str = "", biz_id: str = "") -> list[dict]:
        """列出附件。"""
        logger.info(f"列出附件: type={biz_type}, biz_id={biz_id}")
        return []


attachment_service = AttachmentService()
