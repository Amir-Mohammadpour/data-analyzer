import uuid
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile, status

from app.models.dataset import Dataset, DatasetStatus

UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024
ALLOWED_EXTENSIONS = {".csv"}


def ensure_upload_dir() -> None:
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def validate_file(file: UploadFile) -> None:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )

    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type '{extension}'. Only CSV files are allowed",
        )


def generate_unique_filename(original_filename: str) -> str:
    extension = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex[:8]
    stem = Path(original_filename).stem
    return f"{unique_id}-{stem}{extension}"


async def save_file(file: UploadFile, filename: str) -> int:
    ensure_upload_dir()
    file_path = UPLOAD_DIR / filename
    file_size = 0

    with open(file_path, "wb") as buffer:
        while chunk := await file.read(1024 * 1024):
            file_size += len(chunk)

            if file_size > MAX_FILE_SIZE:
                buffer.close()
                file_path.unlink(missing_ok=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File size exceeds the {MAX_FILE_SIZE // (1024 * 1024)}MB limit",
                )

            buffer.write(chunk)

    return file_size


def process_csv(dataset: Dataset) -> None:
    file_path = UPLOAD_DIR / dataset.filename

    try:
        df = pd.read_csv(file_path)

        dataset.row_count = len(df)
        dataset.column_count = len(df.columns)
        dataset.column_names = df.columns.tolist()
        dataset.status = DatasetStatus.READY

    except Exception as e:
        dataset.status = DatasetStatus.FAILED
        dataset.error_message = f"Failed to process CSV: {str(e)}"
