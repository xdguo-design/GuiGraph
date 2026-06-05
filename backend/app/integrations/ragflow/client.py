"""RAGFlow 客户端封装。"""

import httpx
from loguru import logger

from app.config.settings import settings


class RAGFlowClient:
    """RAGFlow REST API 客户端。"""

    def __init__(self):
        self.base_url = settings.RAGFLOW_URL
        self.api_key = settings.RAGFLOW_API_KEY
        self.headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}

    async def search(self, query: str, dataset_id: str = "") -> list[dict]:
        """语义搜索。"""
        logger.info(f"RAGFlow 搜索: {query}")
        # TODO: 实际调用 RAGFlow API
        return []

    async def upload_document(self, file_bytes: bytes, filename: str, dataset_id: str) -> str:
        """上传文档。"""
        logger.info(f"RAGFlow 上传文档: {filename}")
        # TODO: 实际调用 RAGFlow API
        return "doc_001"

    async def parse_image(self, image_bytes: bytes) -> str:
        """OCR 图片识别。"""
        logger.info("RAGFlow OCR 识别图片")
        # TODO: 实际调用 RAGFlow API
        return "识别结果"


ragflow_client = RAGFlowClient()
