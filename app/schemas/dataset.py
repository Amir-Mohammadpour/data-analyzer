from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.dataset import DatasetStatus


class DatasetBase(BaseModel):
    original_filename: str
    file_size: int


class DatasetResponse(DatasetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    filename: str
    row_count: int | None
    column_count: int | None
    column_names: list[str] | None
    status: DatasetStatus
    error_message: str | None
    created_at: datetime


class DatasetListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    original_filename: str
    file_size: int
    row_count: int | None
    status: DatasetStatus
    created_at: datetime


class DatasetList(BaseModel):
    total: int
    items: list[DatasetListItem] = Field(default_factory=list)
