from __future__ import annotations
import functools
from typing import Optional, Any
from config.settings import settings

try:
    from langfuse.callback import CallbackHandler
    from langfuse.decorators import observe
    HAS_LANGFUSE = True
except ImportError:
    HAS_LANGFUSE = False

def get_langfuse_handler() -> Optional[Any]:
    if HAS_LANGFUSE and settings.langfuse_public_key and settings.langfuse_secret_key:
        return CallbackHandler(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host
        )
    return None

def traced_agent(name: str):
    def decorator(func):
        if HAS_LANGFUSE:
            @observe(name=name)
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            return wrapper
    return decorator
