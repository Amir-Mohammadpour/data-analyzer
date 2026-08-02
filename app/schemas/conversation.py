from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    question: str = Field(min_length=3, max_length=1000)


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dataset_id: int
    question: str
    answer: str
    tokens_used: int | None
    created_at: datetime


class ConversationList(BaseModel):
    total: int
    items: list[ConversationResponse] = Field(default_factory=list)
