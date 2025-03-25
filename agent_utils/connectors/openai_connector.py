import dotenv
import os
from openai import AzureOpenAI
from openai.types.beta import Assistant
from pydantic import BaseModel

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

    # DEPRECATED            
    # async def prompt_assistant(self, assistant_id, prompt, **kwargs):
    #     response_spec = kwargs.get('response_spec', {"type": "json_object"}) # Supply Pydantic model for structured response
        
    #     thread_id = self.get_or_create_thread(message_content=prompt, thread_id=kwargs.get('thread_id', None))
    #     run = self.client.beta.threads.runs.create_and_poll(
    #         thread_id=thread_id, 
    #         assistant_id=assistant_id, 
    #         response_format=response_spec,
    #         poll_interval_ms=1000*60, # 1 minute to avoid rate limiting
    #     )        

    #     if run.status == 'completed':
    #         msg = self.client.beta.threads.messages.list(thread_id=thread_id)
    #         final_output = {"thread_id": thread_id, "msg": msg, "status": run.status, "usage": run.usage.total_tokens}
    #         logging.info(f"Node: {assistant_id} - Assistant status: {run.status} | Usage: {run.usage.total_tokens}")
    #     else:
    #         final_output = {"thread_id": thread_id, "msg": "Non complete status output", "status": "Failed", "usage": run.usage.total_tokens}
    #         logging.error(f"Node: {assistant_id} - Assistant status: {run.status} | Usage: {run.usage.total_tokens} | Error: {run.last_error}")
        
    #     thread_messages = self.client.beta.threads.messages.list(thread_id)
    #     response_json_str = thread_messages.to_dict()['data'][0]['content'][0]['text']['value'] # Always the most recent message
    #     response_json = json.loads(response_json_str)
    #     result = { 
    #         "thread_id": final_output['thread_id'],
    #         "message": response_json,
    #     }
    #     return result
    
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
            #No Async option exists for completions
            completion = self.client.chat.completions.create(
                model = self.deployment,
                messages= prompt_messages,
                response_format=response_spec
            )
            tokens_used = completion.usage.total_tokens
            result = completion.choices[0].message.content

            logging.info(f"Tokens used: {tokens_used}") 
    
            return {"result": json.loads(result), "tokens_used": tokens_used}