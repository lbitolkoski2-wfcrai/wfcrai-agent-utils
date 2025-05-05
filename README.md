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

## Publish new version

### 1. Merge your new branch into main
### 2. Create a new release with a new tag, here is an sample: https://github.com/lbitolkoski2-wfcrai/wfcrai-agent-utils/releases/tag/0.0.2
### 3. The workflow will build and publish to https://us-central1-python.pkg.dev/gcp-wow-food-wfc-ai-dev/wfcrai-agent-utils

## Installation

### 1. Authenticate with Artifact Registry  
Install the keyring helpers so pip can pull from GAR:

```bash
uv add keyrings.google-artifactregistry-auth

# Enable keyring authentication
export UV_KEYRING_PROVIDER=subprocess

# Set the username for the index
export UV_INDEX_PRIVATE_REGISTRY_USERNAME=oauth2accesstoken
```
### 2. Set gcloud project and refresh authentication token

```bash
gcloud auth login --project gcp-wow-food-wfc-ai-dev && gcloud auth application-default login --project gcp-wow-food-wfc-ai-de
```


### 3. Installing agent-utils from gar

```bash
uv add wfcrai-agent-utils --keyring-provider subprocess --index https://oauth2accesstoken@us-central1-python.pkg.dev/gcp-wow-food-wfc-ai-dev/wfcrai-agent-utils/simple/
```
