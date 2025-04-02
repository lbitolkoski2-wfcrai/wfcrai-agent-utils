from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Union, Optional


class ConfluenceTable(BaseModel):
    model_config = ConfigDict(extra='allow')
    overview: str
    table_name: str
    table_id: str
    limitations: str
    notes: str
    key_fields: Dict[str, str]

class ConfluenceBQPage(BaseModel): # dataset or dataset.table name -> confluence data
    bq_resource_type: str #table or dataset
    bq_resource_name: str #dataset_name or dataset_name.table_name
    confluence_page_id: Optional[str] = None # Confluence page ID
    confluence_parent_page_id : Optional[str] = None # if table, parent dataset page ID
    confluence_page_content: Optional[str] = None # Confluence page content
    
class EmailContext(BaseModel):
    task_prompt: str

class Dataset(BaseModel):
    model_config = ConfigDict(extra='allow')
    dataset: str
    table: str

#===== LLM Response Schema =====
class FilterAgentResponse(BaseModel):
    datasets: List[Dataset]

class ConfluenceAgentResponse(BaseModel):
    datasets: List[ConfluenceTable]

class SQLGenAgentResponse(BaseModel):
    sql: str

