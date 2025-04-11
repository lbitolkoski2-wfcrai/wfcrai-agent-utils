from langfuse.decorators import observe, langfuse_context
import asyncio
import os 

import asyncio
import os

def langfuse_wrap_node(func, node_name=None):
    # Get agent name from environment variables
    agent_name = os.getenv("AGENT_NAME", "unknown")

    @observe(name=node_name, capture_input=False, capture_output=False)
    def sync_wrapper(ctx):  
        request_id = ctx.email_context.get("request_id", "unknown")
        # Update the trace with information from the context
        result = func(ctx)
        langfuse_context.update_current_trace(tags=[],
            output=result.agent_context, 
            session_id=request_id,
            metadata={
                "agent_name": agent_name,
            }
        )
        return result
    @observe(name=node_name, capture_input=False, capture_output=False)
    async def async_wrapper(ctx):  
        request_id = ctx.email_context.get("request_id", "unknown")
        result = await func(ctx)
        langfuse_context.update_current_trace(tags=[],
            output=result.agent_context, 
            session_id=request_id,
            metadata={
                "agent_name": agent_name,
            }
        )
        return result
    # Return the appropriate wrapper based on whether the function is async or sync
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper

