import uuid
from collections.abc import Generator
from pathlib import Path
from time import sleep
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app.ents import Base, Task
from app.infra.db.engine import engine
from app.infra.depends.db import get_db
from app.infra.depends.r2 import get_r2
from app.main import app

taskId = uuid.uuid4()


@pytest.fixture
def setup() -> Generator[TestClient]:
    # Create tables
    Base.metadata.create_all(bind=engine)

    # Seed
    db = next(get_db())
    db.add(Task(id=taskId))
    db.commit()
    db.close()

    def mock_get_r2() -> MagicMock:
        return MagicMock()

    app.dependency_overrides[get_r2] = mock_get_r2

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.mark.e2e
def test_can_get_task_status(setup: TestClient) -> None:
    """タスクのstatusを取得できる"""
    # Arrange
    client = setup

    # Act
    res = client.get(f"/v1/task/status/{taskId}")

    # Assert
    assert res.status_code == HTTP_200_OK
    assert res.json()["id"] == str(taskId)


@pytest.mark.e2e
def test_badrequest_on_not_found_task(setup: TestClient) -> None:
    """存在しないタスクの場合には400"""
    # Arrange
    client = setup

    # Act
    res = client.get(f"/v1/task/status/{uuid.uuid4()!s}")

    # Assert
    assert res.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.e2e
def test_can_detect_cat(setup: TestClient) -> None:
    """猫を検出できる"""
    # Arrange
    client = setup
    with Path("fixtures/cat.jpg").open("rb") as f:
        files = {"file": ("cat.jpg", f, "image/jpeg")}
        # Act
        res = client.post("/v1/yolo/detect/cat", files=files)

    # Assert
    assert res.status_code == HTTP_200_OK
    targetTaskId = res.json()["id"]
    assert len(targetTaskId) > 0

    sleep(0.1)

    # Act2
    taskRes = client.get(f"/v1/task/status/{targetTaskId}")

    # Assert2
    assert taskRes.status_code == HTTP_200_OK
    taskData = taskRes.json()
    assert taskData["status"] == "detect_cat:finished"
    assert taskData["hasCat"]


@pytest.mark.e2e
def test_can_handle_wo_cat(setup: TestClient) -> None:
    """猫が検出できない場合"""
    # Arrange
    client = setup
    with Path("fixtures/not-cat.jpg").open("rb") as f:
        files = {"file": ("cat.jpg", f, "image/jpeg")}
        # Act
        res = client.post("/v1/yolo/detect/cat", files=files)

    # Assert
    assert res.status_code == HTTP_200_OK
    targetTaskId = res.json()["id"]
    assert len(targetTaskId) > 0

    sleep(0.1)

    # Act2
    taskRes = client.get(f"/v1/task/status/{targetTaskId}")

    # Assert2
    assert taskRes.status_code == HTTP_200_OK
    taskData = taskRes.json()
    assert taskData["status"] == "detect_cat:finished"
    assert not taskData["hasCat"]


@pytest.mark.e2e
def test_can_trim_all_cat(setup: TestClient) -> None:
    """存在する猫をトリミングできる"""
    # Arrange
    client = setup
    with Path("fixtures/cat.jpg").open("rb") as f:
        files = {"file": ("cat.jpg", f, "image/jpeg")}
        # Act
        res = client.post("/v1/yolo/trim/cat", files=files)

    # Assert
    assert res.status_code == HTTP_200_OK
    targetTaskId = res.json()["id"]
    assert len(targetTaskId) > 0

    sleep(0.3)

    # Act2
    taskRes = client.get(f"/v1/task/status/{targetTaskId}")

    # Assert2
    assert taskRes.status_code == HTTP_200_OK
    taskData = taskRes.json()
    assert taskData["status"] == "trim_cat:finished"
    assert taskData["hasCat"]
    # cropしていない元画像も上げるので、猫数+1となる
    assert len(taskData["cats"]) == 2


@pytest.mark.e2e
def test_stop_till_detect_wo_cat(setup: TestClient) -> None:
    """猫がいない場合には、猫検出でstopする"""
    # Arrange
    client = setup
    with Path("fixtures/not-cat.jpg").open("rb") as f:
        files = {"file": ("cat.jpg", f, "image/jpeg")}
        # Act
        res = client.post("/v1/yolo/trim/cat", files=files)

    # Assert
    assert res.status_code == HTTP_200_OK
    targetTaskId = res.json()["id"]
    assert len(targetTaskId) > 0

    sleep(0.3)

    # Act2
    taskRes = client.get(f"/v1/task/status/{targetTaskId}")

    # Assert2
    assert taskRes.status_code == HTTP_200_OK
    taskData = taskRes.json()
    assert taskData["status"] == "detect_cat:finished"
    assert not taskData["hasCat"]


@pytest.mark.e2e
def test_can_classify_cat_activity(setup: TestClient) -> None:
    """猫の活動を分類できる"""
    # Arrange
    client = setup
    labels = [
        "eating cat",
        "grooming cat",
        "scratching cat",
        "sleeping cat",
    ]

    with Path("fixtures/scratching-cat.jpeg").open("rb") as f:
        # Act
        res = client.post(
            "/v1/clip/classify/cat/activity",
            files={"file": ("scratching-cat.jpeg", f, "image/jpeg")},
            data={"labels": labels},
        )

    # Assert
    assert res.status_code == HTTP_200_OK
    body = res.json()
    assert body["mostLikelyLabel"] == "scratching cat"
    assert len(body["results"]) == len(labels)
    result_labels = {r["label"] for r in body["results"]}
    assert result_labels == set(labels)


@pytest.mark.e2e
def test_badrequest_on_invalid_image_for_clip(setup: TestClient) -> None:
    """無効な画像には400を返す"""
    # Arrange
    client = setup

    # Act
    res = client.post(
        "/v1/clip/classify/cat/activity",
        files={"file": ("invalid.jpg", b"not-an-image", "image/jpeg")},
        data={"labels": ["eating", "sleeping"]},
    )

    # Assert
    assert res.status_code == HTTP_400_BAD_REQUEST
