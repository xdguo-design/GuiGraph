"""多数据库方言抽象基类。"""

from abc import ABC, abstractmethod


class BaseDialect(ABC):
    """数据库方言抽象接口。"""

    @staticmethod
    @abstractmethod
    def get_auto_increment_sql() -> str:
        """获取自增主键的 SQL 语法。"""
        pass

    @staticmethod
    @abstractmethod
    def get_limit_offset_sql(limit: int, offset: int) -> str:
        """获取分页 SQL 语法。"""
        pass

    @staticmethod
    @abstractmethod
    def get_sequence_name(table_name: str) -> str:
        """获取序列名称（适用于 Oracle/PostgreSQL）。"""
        pass

    @staticmethod
    @abstractmethod
    def get_current_timestamp() -> str:
        """获取当前时间戳的 SQL 函数。"""
        pass

    @staticmethod
    @abstractmethod
    def get_table_comment_sql(table_name: str, comment: str) -> str:
        """获取添加表注释的 SQL。"""
        pass
