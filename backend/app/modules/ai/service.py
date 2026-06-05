"""AI 能力模块服务层。"""

from loguru import logger


class AIService:
    """AI 业务逻辑。"""

    async def rag_search(self, query: str) -> list[dict]:
        """RAG 语义搜索。"""
        logger.info(f"RAG 搜索: {query}")
        return []

    async def generate_summary(self, content: str) -> str:
        """生成总结。"""
        logger.info(f"生成总结: {content[:50]}")
        return "总结内容"


ai_service = AIService()
