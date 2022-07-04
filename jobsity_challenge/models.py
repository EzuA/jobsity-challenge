from pydantic import BaseModel


class Table(BaseModel):
    schema_name: str
    table_name: str

    def __str__(self) -> str:
        return f"{self.schema_name}.{self.table_name}"


class ApiInputConfig(BaseModel):
    full_load: bool
    init_db: bool = False


class ApiInputBoundingBox(BaseModel):
    lon_min: float
    lat_min: float
    lon_max: float
    lat_max: float
    srid: int = 4326
