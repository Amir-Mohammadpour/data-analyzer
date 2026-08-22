import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_upload_requires_authentication(client: AsyncClient):
    files = {"file": ("test.csv", b"name,age\nAlice,30\n", "text/csv")}

    response = await client.post("/api/v1/datasets/upload", files=files)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_upload_invalid_file_type(authenticated_client: AsyncClient):
    files = {"file": ("test.txt", b"just some text", "text/plain")}

    response = await authenticated_client.post("/api/v1/datasets/upload", files=files)

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_upload_success(authenticated_client: AsyncClient):
    csv_content = b"name,age\nAlice,30\nBob,25\nCharlie,35\n"
    files = {"file": ("people.csv", csv_content, "text/csv")}

    response = await authenticated_client.post("/api/v1/datasets/upload", files=files)

    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ready"
    assert data["row_count"] == 3
    assert data["column_count"] == 2


@pytest.mark.asyncio
async def test_list_datasets(authenticated_client: AsyncClient):
    csv_content = b"name,age\nAlice,30\n"

    await authenticated_client.post(
        "/api/v1/datasets/upload",
        files={"file": ("first.csv", csv_content, "text/csv")},
    )
    await authenticated_client.post(
        "/api/v1/datasets/upload",
        files={"file": ("second.csv", csv_content, "text/csv")},
    )

    response = await authenticated_client.get("/api/v1/datasets")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
