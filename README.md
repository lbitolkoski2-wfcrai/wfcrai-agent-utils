# Agent Utils

This directory contains utility functions and classes for the WFCRAI agents project. These utilities are designed to support the main functionalities of the agents by providing common operations, helper functions, and shared resources.



## Directory Structure

```
agent_utils/
├── components/ #General helper functions
├── connectors/ #External access (api etc)
```

# Connectors

The `connectors` directory contains modules that facilitate external access and integrations. Below is a brief description of each file:

- `bq_connector.py`: Connector for BigQuery.
- `confluence_connector.py`: Connector for Confluence.
- `gcs_connector.py`: Connector for Google Cloud Storage.
- `llm_connector.py`:   Wrapper for connecting to LLMs with system/user prompt API.
- `openai_connector.py`: Connector for OpenAI services (don't use directly)


# Components
## Assistant 

`components/assistant` is a helper class designed to perform LLM (Large Language Model) calls using assistants. It provides a structured way to initialize and run assistants with the required context and configuration.

### Methods

- `__init__(self, llm_connector, config)`: Initializes the Assistant with the LLM connector and configuration.
- `async def run_assistant(self, ctx, prompt_key, response_schema, additional_context)`: Runs the assistant with the provided context, prompt key, response schema, and additional context.

### Config

example

```toml
[prompts]
[prompts.confluence_context]
instructions = "Your task is to find all relevant information from the....."
task = "Summarize the following HTML content {confluence_html_content}"
```


### Arguments
- `ctx (dict)`: The graph state.
- `prompt_key (str)`: Key to load the prompt from config. ex. `confluence_context`
- `response_schema (pydantic model)`: The schema for the response from the assistant.
- `additional_context (dict)`: Additional context `[Dict[str,str]]` for formatting the prompt with required context.

### Returns

- `dict`: A dictionary containing the results and the number of tokens used.
  - `results (dict)`: The formatted prompt and the JSON response from the assistant conforming to the response schema.
  - `tokens_used (int)`: The number of tokens used in the assistant call.