"""PostgreSQL 方言实现。"""

from .base_dialect import BaseDialect


class PostgreSQLDialect(BaseDialect):
    """PostgreSQL 14+ 方言。"""

    @staticmethod
    def get_auto_increment_sql() -> str:
        return "SERIAL"

    @staticmethod
    def get_limit_offset_sql(limit: int, offset: int) -> str:
        return f"LIMIT {limit} OFFSET {offset}"

    @staticmethod
    def get_sequence_name(table_name: str) -> str:
        return f"{table_name}_id_seq"

    @staticmethod
    def get_current_timestamp() -> str:
        return "CURRENT_TIMESTAMP"

    @staticmethod
    def get_table_comment_sql(table_name: str, comment: str) -> str:
        return f"COMMENT ON TABLE {table_name} IS '{comment}'"
