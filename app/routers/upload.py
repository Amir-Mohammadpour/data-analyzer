from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_owned_dataset
from app.database import get_db
from app.models import Dataset, User
from app.schemas import DatasetList, DatasetListItem, DatasetResponse
from app.services.file_service import (
    generate_unique_filename,
    process_csv,
    save_file,
    validate_file,
)

router = APIRouter(prefix="/api/v1/datasets", tags=["Datasets"])


@router.post(
    "/upload", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED
)
async def upload(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> Dataset:
    validate_file(file)
    filename = generate_unique_filename(file.filename)
    file_size = await save_file(file, filename)
    dataset = Dataset(
        user_id=current_user.id,
        filename=filename,
        original_filename=file.filename,
        file_size=file_size,
    )

    db.add(dataset)
    await db.flush()
    process_csv(dataset)
    await db.flush() 
    await db.refresh(dataset)
    return dataset


@router.get("", response_model=DatasetList)
async def dataset_list(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DatasetList:
    result = await db.execute(
        select(Dataset)
        .where(Dataset.user_id == current_user.id)
        .order_by(Dataset.created_at.desc())
    )
    datasets = result.scalars().all()

    items = [DatasetListItem.model_validate(dataset) for dataset in datasets]
    return DatasetList(total=len(datasets), items=items)


@router.get("/{dataset_id}", response_model=DatasetResponse)
async def get_dataset(
    dataset: Dataset = Depends(get_owned_dataset),
)-> Dataset:
    return dataset
