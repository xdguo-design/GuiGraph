"""Prompt 模板引擎：从数据库加载模板并渲染变量。"""

import re
from typing import Any

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.model_manager.models import AiPromptTemplate

# ── 内置默认 Prompt 模板（数据库为空时回退使用） ──────────────

DEFAULT_TEMPLATES: dict[str, str] = {
    "change_doc_generator": """你是一个专业的变更管理文档工程师。

请根据以下变更信息，生成一份规范的变更说明书，包含：
1. 变更概述
2. 变更原因
3. 影响范围分析
4. 涉及的数据库表/API
5. 回滚方案建议
6. 风险评估（高/中/低）

变更信息：
{{changes}}

请用 Markdown 格式输出。""",

    "change_impact_analysis": """你是一个资深的系统架构师，擅长分析变更影响范围。

请分析以下变更可能影响的范围：
- 数据库表和字段
- API 接口
- 相关服务
- 下游依赖

变更内容：{{content}}
变更类型：{{change_type}}
影响范围（用户填写）：{{effect_scope}}

请以 JSON 格式输出分析结果：
{
  "impact_tables": ["表名列表"],
  "impact_apis": ["API 列表"],
  "impact_services": ["服务列表"],
  "risk_level": "high/medium/low",
  "suggestion": "补充建议"
}""",

    "smart_search": """基于以下上下文信息，回答用户的问题。如果上下文信息不足，请说明需要哪些额外信息。

上下文：
{{context}}

用户问题：{{query}}

请给出清晰、准确的回答。""",

    "dashboard_insight": """你是一个数据分析助手。请根据以下仪表盘数据，给出 3-5 条关键洞察和建议。

数据摘要：
{{dashboard_data}}

请按以下格式输出每条洞察：
- **洞察标题**：描述 + 建议动作""",

    "auto_tag_note": """请为以下笔记内容推荐 3-5 个标签。

笔记标题：{{title}}
笔记内容：
{{content}}

请以 JSON 数组格式输出标签：["标签1", "标签2", "标签3"]""",

    "build_diagnosis": """你是一个 DevOps 专家。请分析以下构建日志，找出失败根因并给出修复建议。

构建日志：
{{build_log}}

请输出：
1. **失败根因**：一句话总结
2. **详细分析**：逐行分析关键错误
3. **修复建议**：具体的修复步骤""",

    "commit_message_gen": """请根据以下代码 diff 生成一条规范的 Git commit 消息。

要求：
- 使用 Conventional Commits 格式（feat/fix/refactor/docs/chore 等）
- 第一行不超过 72 字符
- 如有必要，添加简短的正文说明

代码 Diff：
{{diff_text}}

只输出 commit 消息，不要其他内容。""",

    "code_review": """你是一个资深的代码审查专家。请审查以下代码变更，给出专业的 Review 意见。

代码变更：
{{diff_text}}

请从以下维度审查：
1. **正确性**：逻辑是否正确
2. **安全性**：是否有安全风险
3. **性能**：是否有性能问题
4. **可维护性**：代码是否清晰易读

按严重程度分级输出：🔴 严重 / 🟡 建议 / 🟢 良好""",

    "merge_conflict_solve": """你是一个 Git 合并冲突解决专家。请分析以下冲突内容并给出解决方案。

冲突内容：
{{conflict_text}}

请输出：
1. 冲突原因分析
2. 推荐的解决方案（保留哪一方或如何合并）
3. 解决后的完整代码""",

    "summary": """请对以下内容生成一份简洁的摘要，不超过 200 字。

内容：
{{content}}

摘要：""",
}


class PromptEngine:
    """Prompt 模板引擎。"""

    def render(self, template_str: str, variables: dict[str, Any]) -> str:
        """渲染模板：将 {{var}} 替换为变量值。"""
        def replacer(match: re.Match) -> str:
            key = match.group(1)
            value = variables.get(key, f"{{{{{key}}}}}")
            return str(value)

        return re.sub(r"\{\{(\w+)\}\}", replacer, template_str)

    async def get_template(self, db: AsyncSession, scenario: str) -> str:
        """从数据库加载激活的模板，无则回退到内置默认。"""
        stmt = (
            select(AiPromptTemplate)
            .where(
                AiPromptTemplate.scenario == scenario,
                AiPromptTemplate.is_active == True,  # noqa: E712
            )
            .order_by(AiPromptTemplate.id.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        record = result.scalar_one_or_none()
        if record:
            return record.template

        # 回退到内置默认
        default = DEFAULT_TEMPLATES.get(scenario, "")
        if not default:
            logger.warning(f"未找到场景 {scenario} 的 Prompt 模板")
        return default


# 全局单例
prompt_engine = PromptEngine()
