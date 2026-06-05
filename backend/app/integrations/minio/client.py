"""MinIO 客户端封装。"""

import io
from pathlib import Path

from minio import Minio
from minio.error import S3Error

from app.config.settings import settings


class MinioClient:
    """MinIO 客户端封装。"""

    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )

    def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """上传文件。"""
        try:
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=io.BytesIO(data),
                length=len(data),
                content_type=content_type,
            )
            return f"{settings.MINIO_ENDPOINT}/{bucket_name}/{object_name}"
        except S3Error as e:
            raise RuntimeError(f"MinIO 上传失败: {e}")

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        """下载文件。"""
        try:
            response = self.client.get_object(bucket_name, object_name)
            return response.read()
        except S3Error as e:
            raise RuntimeError(f"MinIO 下载失败: {e}")

    def get_presigned_url(self, bucket_name: str, object_name: str, expires: int = 3600) -> str:
        """获取签名 URL。"""
        return self.client.presigned_get_object(bucket_name, object_name, expires=expires)

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        """删除文件。"""
        self.client.remove_object(bucket_name, object_name)

    def bucket_exists(self, bucket_name: str) -> bool:
        """检查桶是否存在。"""
        return self.client.bucket_exists(bucket_name)

    def create_bucket(self, bucket_name: str) -> None:
        """创建桶。"""
        if not self.bucket_exists(bucket_name):
            self.client.make_bucket(bucket_name)


minio_client = MinioClient()
