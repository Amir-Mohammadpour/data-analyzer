from httpx import AsyncClient

from app.routers import analyze


async def fake_ask_ai(context: str, question: str) -> tuple[str, int | None]:
    return "This is a fake AI answer for testing.", 42


async def test_ask_question_success(authenticated_client: AsyncClient, monkeypatch):
    monkeypatch.setattr("app.routers.analyze.ask_ai", fake_ask_ai)

    csv_content = b"name,age\nAlice,30\nBob,25\n"
    upload_response = await authenticated_client.post(
        "/api/v1/datasets/upload",
        files={"file": ("people.csv", csv_content, "text/csv")},
    )
    dataset_id = upload_response.json()["id"]

    response = await authenticated_client.post(
        f"/api/v1/datasets/{dataset_id}/conversations",
        json={"question": "How many rows are there?"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["answer"] == "This is a fake AI answer for testing."
    assert data["question"] == "How many rows are there?"
    assert data["tokens_used"] == 42


async def test_ask_question_dataset_not_ready(
    authenticated_client: AsyncClient, monkeypatch
):
    monkeypatch.setattr("app.routers.analyze.ask_ai", fake_ask_ai)

    upload_response = await authenticated_client.post(
        "/api/v1/datasets/upload",
        files={"file": ("broken.csv", b"", "text/csv")},
    )
    dataset_id = upload_response.json()["id"]

    response = await authenticated_client.post(
        f"/api/v1/datasets/{dataset_id}/conversations",
        json={"question": "Anything?"},
    )

    assert response.status_code == 400


async def test_ask_question_nonexistent_dataset(
    authenticated_client: AsyncClient, monkeypatch
):
    monkeypatch.setattr("app.routers.analyze.ask_ai", fake_ask_ai)

    response = await authenticated_client.post(
        "/api/v1/datasets/999/conversations",
        json={"question": "Anything?"},
    )

    assert response.status_code == 404


async def test_get_conversations(authenticated_client: AsyncClient, monkeypatch):
    monkeypatch.setattr("app.routers.analyze.ask_ai", fake_ask_ai)

    csv_content = b"name,age\nAlice,30\n"
    upload_response = await authenticated_client.post(
        "/api/v1/datasets/upload",
        files={"file": ("people.csv", csv_content, "text/csv")},
    )
    dataset_id = upload_response.json()["id"]

    await authenticated_client.post(
        f"/api/v1/datasets/{dataset_id}/conversations",
        json={"question": "First question?"},
    )
    await authenticated_client.post(
        f"/api/v1/datasets/{dataset_id}/conversations",
        json={"question": "Second question?"},
    )

    response = await authenticated_client.get(
        f"/api/v1/datasets/{dataset_id}/conversations"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
