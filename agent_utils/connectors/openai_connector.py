import dotenv
import os
from langfuse.openai import AzureOpenAI
from openai.types.beta import Assistant
from pydantic import BaseModel
# from langfuse.decorators import observe
from langfuse.decorators import observe, langfuse_context
import time
import json
import logging

class OpenAIConnector():
    def __init__(self, config=None):
        self.config = config
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.api_url = os.getenv('OPENAI_API_URL')
        self.api_version = os.getenv('OPENAI_API_VERSION')
        self.deployment = config['llm_connector']['openai']['deployment']
        self.create_connection()

    def create_connection(self):
        client = AzureOpenAI()
        self.client = client

    def get_or_create_thread(self, message_content, thread_id=None):
        if not thread_id:
            thread = self.client.beta.threads.create(
                messages=[{"role": "user", "content": message_content}]
            )
            return thread.id
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message_content
        )
        return thread_id

    async def prompt(self,prompts:dict, response_spec: BaseModel = None, **kwargs):
            """
            Entrypoint for email requests routed to the data-agent"
            prompts = [
                {"system_prompt": "You are a SQL expert...."},
                {"user_prompt": "I need to know the total sales by CREST segment"}
            ]
            """
            response_spec = response_spec if response_spec is not None else {"type": "json_object"}
        
            prompt_messages = [
                {"role": "system", "content": prompts['system_prompt']},
                {"role": "user", "content": prompts['user_prompt']}
            ]
            
            langfuse_params = kwargs.get('langfuse_params', {})
            tags = langfuse_params.get('tags', [])

            def log_completion(prompt_messages):
                return self.client.chat.completions.create(
                    model = self.deployment,
                    messages= prompt_messages,
                    response_format=response_spec
                )
            completion = log_completion(prompt_messages)
            tokens_used = completion.usage.total_tokens
            result = completion.choices[0].message.content

            logging.info(f"Tokens used: {tokens_used}") 
    
            return {"result": json.loads(result), "tokens_used": tokens_used}