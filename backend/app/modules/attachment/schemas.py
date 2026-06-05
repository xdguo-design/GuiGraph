"""附件模块 Schema 定义。"""

from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """文件上传响应。"""
    file_id: str
    file_url: str
    file_name: str
    file_size: int
    biz_type: str
    biz_id: str


class FileInfo(BaseModel):
    """文件信息。"""
    id: str
    biz_type: str
    biz_id: str
    file_type: str
    file_name: str
    file_size: int
    upload_time: str
    uploaded_by: str
