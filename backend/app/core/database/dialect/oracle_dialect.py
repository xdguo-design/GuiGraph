"""Oracle 方言实现。"""

from .base_dialect import BaseDialect


class OracleDialect(BaseDialect):
    """Oracle 19c+ 方言。"""

    @staticmethod
    def get_auto_increment_sql() -> str:
        return "IDENTITY"

    @staticmethod
    def get_limit_offset_sql(limit: int, offset: int) -> str:
        return f"FETCH NEXT {limit} ROWS ONLY OFFSET {offset} ROWS"

    @staticmethod
    def get_sequence_name(table_name: str) -> str:
        return f"{table_name}_SEQ"

    @staticmethod
    def get_current_timestamp() -> str:
        return "SYSTIMESTAMP"

    @staticmethod
    def get_table_comment_sql(table_name: str, comment: str) -> str:
        return f"COMMENT ON TABLE {table_name} IS '{comment}'"
