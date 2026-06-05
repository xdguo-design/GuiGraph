"""MySQL 方言实现。"""

from .base_dialect import BaseDialect


class MySQLDialect(BaseDialect):
    """MySQL 8+ 方言。"""

    @staticmethod
    def get_auto_increment_sql() -> str:
        return "AUTO_INCREMENT"

    @staticmethod
    def get_limit_offset_sql(limit: int, offset: int) -> str:
        return f"LIMIT {limit} OFFSET {offset}"

    @staticmethod
    def get_sequence_name(table_name: str) -> str:
        # MySQL 不使用序列
        return ""

    @staticmethod
    def get_current_timestamp() -> str:
        return "NOW()"

    @staticmethod
    def get_table_comment_sql(table_name: str, comment: str) -> str:
        return f"ALTER TABLE {table_name} COMMENT = '{comment}'"
