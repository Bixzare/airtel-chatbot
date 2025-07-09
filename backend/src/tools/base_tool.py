"""
Base tool interface for agent tools.
"""

from typing import Any

class BaseTool:
    """Base interface for agent tools."""
    name: str
    description: str

    def __call__(self, *args, **kwargs) -> Any:
        raise NotImplementedError("Tool must implement __call__ method.") 