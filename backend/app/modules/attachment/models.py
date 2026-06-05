"""附件模块 ORM 模型。"""

from sqlalchemy import String, Integer, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database.base import Base
from app.shared.enums import BizFileType, FileAttachmentType


class BizAttachFile(Base):
    """附件表。"""
    __tablename__ = "biz_attach_file"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    biz_type: Mapped[BizFileType] = mapped_column(Enum(BizFileType), nullable=False, comment="业务类型")
    biz_id: Mapped[int] = mapped_column(Integer, nullable=False, comment="业务 ID")
    file_type: Mapped[FileAttachmentType] = mapped_column(Enum(FileAttachmentType), nullable=False, comment="文件类型")
    minio_bucket: Mapped[str] = mapped_column(String(100), nullable=False, comment="MinIO 桶名")
    minio_path: Mapped[str] = mapped_column(String(500), nullable=False, comment="MinIO 对象路径")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, comment="文件大小（字节）")
    upload_time: Mapped[DateTime] = mapped_column(DateTime, nullable=False, comment="上传时间")
    uploaded_by: Mapped[int] = mapped_column(Integer, nullable=False, comment="上传人 ID")

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "biz_type": self.biz_type.value,
            "biz_id": str(self.biz_id),
            "file_type": self.file_type.value,
            "minio_bucket": self.minio_bucket,
            "minio_path": self.minio_path,
            "file_size": self.file_size,
            "upload_time": self.upload_time.isoformat() if self.upload_time else None,
            "uploaded_by": str(self.uploaded_by),
        }
