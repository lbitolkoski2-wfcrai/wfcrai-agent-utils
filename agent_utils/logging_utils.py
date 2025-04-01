from langfuse.decorators import observe, langfuse_context
import asyncio
import os 

def observe_with_tags(tags=[]):
    def decorator(func):
        @observe
        async def wrapper(*args, **kwargs):
            langfuse_context.update_current_trace(tags=tags, metadata={
                "agent_name": os.getenv("AGENT_NAME", "unknown")
            })
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator

