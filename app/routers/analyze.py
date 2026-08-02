from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_owned_dataset
from app.database import get_db
from app.models import Conversation, Dataset
from app.models.dataset import DatasetStatus
from app.schemas import (
    ConversationCreate,
    ConversationList,
    ConversationResponse,
)
from app.services.ai_service import ask_ai
from app.services.file_service import UPLOAD_DIR
from app.services.pandas_service import build_dataframe_context

router = APIRouter(prefix="/api/v1/datasets", tags=["Analyze"])


@router.post(
    "/{dataset_id}/conversations",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def ask_question(
    question_data: ConversationCreate,
    dataset: Dataset = Depends(get_owned_dataset),
    db: AsyncSession = Depends(get_db),
) -> Conversation:
    if dataset.status != DatasetStatus.READY:
        detail = f"Dataset is not ready for analysis (status: {dataset.status.value})"
        if dataset.status == DatasetStatus.FAILED and dataset.error_message:
            detail += f" - {dataset.error_message}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

    file_path = UPLOAD_DIR / dataset.filename
    context = build_dataframe_context(file_path)

    answer, tokens_used = await ask_ai(context, question_data.question)

    conversation = Conversation(
        dataset_id=dataset.id,
        question=question_data.question,
        answer=answer,
        tokens_used=tokens_used,
    )

    db.add(conversation)
    await db.flush()
    await db.refresh(conversation)

    return conversation


@router.get(
    "/{dataset_id}/conversations",
    response_model=ConversationList,
)
async def get_conversations(
    dataset: Dataset = Depends(get_owned_dataset),
    db: AsyncSession = Depends(get_db),
) -> ConversationList:
    result = await db.execute(
        select(Conversation)
        .where(Conversation.dataset_id == dataset.id)
        .order_by(Conversation.created_at.desc())
    )
    conversations = result.scalars().all()

    items = [ConversationResponse.model_validate(c) for c in conversations]
    return ConversationList(total=len(conversations), items=items)
