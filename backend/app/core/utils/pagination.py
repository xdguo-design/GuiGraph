"""分页工具。"""

from typing import Any, Generic, TypeVar

T = TypeVar("T")


def paginate(items: list[T], page: int = 1, page_size: int = 20) -> dict[str, Any]:
    """对列表进行分页。"""
    total = len(items)
    total_pages = (total + page_size - 1) // page_size
    start = (page - 1) * page_size
    end = start + page_size

    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
