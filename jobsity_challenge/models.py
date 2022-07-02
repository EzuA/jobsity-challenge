from pydantic import BaseModel


class IngestionConfig(BaseModel):
    landing_file: str
    schema_name: str
    table_name: str
    pre_action: str
    action: str
