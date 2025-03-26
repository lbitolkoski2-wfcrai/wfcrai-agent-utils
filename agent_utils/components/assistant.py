import logging

class Assistant:
    """
    Helper class to perform LLM Calls using Assistants
    """
    def __init__(self, llm_connector, config):
        self.llm_connector = llm_connector
        self.config = config
    
    async def run_assistant(self, ctx, prompt_key, response_schema, additional_context):
        """"
        Initializes the Assistant with the required context and configuration
        args:
            ctx (dict): The graph state
            prompt_key (str): the key for the prompt configuration
            response_schema (pydantic model): The schema for the response from the assistant
            additional_context (dict): Additional context to be passed to the assistant for formatting the prompt
        returns:
            {
                "prompt": formatted prompt,
                "response": JSON response from the assistant
            }
            The response from the assistant conforming to the response_schema
        """
        base_prompt = self.config['prompts'][prompt_key]['task']
        task_prompt = ctx.email_context['task_prompt'] # Users email request
        
        prompts = {
            "user_prompt": base_prompt.format(task_prompt=task_prompt, **additional_context),
            "system_prompt": self.config['prompts'][prompt_key]['instructions']
        }
        
        logging.info(f"Running assistant: {prompt_key}  with prompt: {prompts['user_prompt']}")
        response_spec = {"type": "json_schema",
            "json_schema": {
                "name": f"{prompt_key}_response_schema",
                "schema": response_schema.model_json_schema()
            }
        }
        response = await self.llm_connector.prompt(ctx,prompts,response_spec)
        return {
            "task": task_prompt,
            "system_prompt": prompts['system_prompt'],
            "user_prompt": prompts['user_prompt'],
            "response": response
        }