#Wrapper Interface for LLM Connectors (OpenAI, Gemini)
import agent_utils.connectors.openai_connector as openai_connector

class LLMConnector:
    def __init__(self, config, connector_type):
        match connector_type:
            case "openai":
                self.openai_connector = openai_connector.OpenAIConnector(config)
            # case "gemini":
            #     self.gemini_connector = gemini.GeminiConnector(config)
            case _:
                raise Exception("Invalid Connector Type")
        self.connector_type = connector_type

    def prompt(self, ctx, prompts:dict, response_schema, **kwargs):
        system_prompt = prompts['system_prompt']
        user_prompt = prompts['user_prompt']

        if self.connector_type == "openai":
            return self.openai_connector.prompt(prompts, response_schema, **kwargs)
        # elif self.connector_type == "gemini":
        #     return self.gemini_connector.prompts(ctx, assistant_name, response_schema, additional_context)
        else:
            raise Exception("Invalid Connector Type")