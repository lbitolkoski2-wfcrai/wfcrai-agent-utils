import logging
import hashlib
from agent_utils.connectors.fs_connector import FirestoreConnector
from pydantic import BaseModel
from agent_utils.schemas.models import AssistantResponse
import os

class Assistant:
    """
    Helper class to perform LLM Calls across different connectors (OpenAI, Gemini)
    This class is used to retrieve prompts, format them with context, and call the LLM.
    It also handles caching of and formatting of the response.
    """
    def __init__(self, llm_connector, config):
        self.llm_connector = llm_connector
        self.fs_connector = FirestoreConnector()
        self.config = config

    async def run_assistant(self, ctx, prompt_key, response_schema: BaseModel, additional_context: dict, cache=False):
        """"
        Initializes the Assistant with the required context and configuration
        args:
            ctx (dict): The graph state
            prompt_key (str): the key for the prompt configuration 
            response_schema (pydantic model): The schema for the response from the assistant
            additional_context (dict): Additional context to be passed to the assistant for formatting the prompt
            cache (bool): Whether to cache and use cached response or not
        returns: 
            return schemas.model.AssistantResponse
        """
        additional_context ['task_prompt'] = ctx.email_context['task_prompt']
        prompts = self._get_formatted_prompts(prompt_key, additional_context)
        hash_key = self._generate_hash_key(prompts) if cache else None

        if cache and (cached_response := self._get_cached_response(hash_key)):
            logging.info(f"Using cached response for key: {hash_key}")
            return cached_response

        logging.info(f"Running assistant: {prompt_key} with prompt: {prompts['user_prompt'][:100]}")
        langfuse_params = {
            "tags" : [os.getenv("AGENT_NAME", "agent_uknown")],
            "request_id": ctx.email_context['request_id'],
            "name": prompt_key
        }
        response = await self.llm_connector.prompt(ctx, prompts, self._response_spec(response_schema, prompt_key), langfuse_params=langfuse_params)
        result = AssistantResponse(**prompts, response=response)

        if cache:

            self.fs_connector.create_document("llm_cache", hash_key, result.model_dump())
        
        return result.model_dump()

    def _get_formatted_prompts(self, prompt_key, additional_context):
        prompts = {
            "system_prompt": self.config['prompts'][prompt_key]['instructions'],
            "user_prompt": self.config['prompts'][prompt_key]['task'].format(**additional_context)
        }
        return prompts

    def _generate_hash_key(self, prompts):
        return hashlib.md5((prompts['user_prompt'] + prompts['system_prompt']).encode()).hexdigest()

    def _get_cached_response(self, hash_key):
        cached_result = self.fs_connector.get_document("llm_cache", hash_key)
        if cached_result:
            logging.info(f"Cache hit for key: {hash_key}")
            return AssistantResponse(**cached_result).model_dump()
        logging.info(f"Cache miss for key: {hash_key}")
        return None
    
    def _response_spec(self, response_schema: BaseModel, prompt_key: str):
        return {"type": "json_schema",
            "json_schema": {
                "name": f"{prompt_key}_response_schema",
                "schema": response_schema.model_json_schema()
            }
        }