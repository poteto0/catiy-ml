[group("ci")]
fmt:
  @uv run ruff format .

[group("ci")]
fmt-check:
  @uv run ruff format --check

[group("ci")]
lint:
  @uv run ruff check .

[group("ci")]
check:
  @uv run ty check

[group("ci")]
ut-cov:
  @ENV=TEST uv run pytest --cov --cov-report=xml --cov-report=term -m "not e2e"

[group("ci")]
ut:
  @ENV=TEST uv run pytest -m "not e2e"

[group("ci")]
e2e:
  @ENV=TEST uv run pytest -m "e2e"

[group("ci")]
ci: fmt lint check ut e2e

# ワークフロー用 e2eを実行しない&フォーマットしない
[group("ci")]
ci-check: fmt-check lint check ut

[group("develop")]
task-status +taskId:
  @curl -X 'GET' \
      'http://localhost:8080/v1/task/status/{{taskId}}' \
      -H 'accept: application/json'

[group("develop")]
detect-cat:
  @curl -X 'POST' \
      'http://localhost:8080/v1/yolo/detect/cat' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@./fixtures/cat.jpg;type=image/jpeg'

[group("develop")]
trimming-cat:
  @curl -X 'POST' \
      'http://localhost:8080/v1/yolo/trim/cat' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'file=@./fixtures/cat.jpg;type=image/jpeg'

[group("develop")]
classify-cat-activity:
  @curl -X 'POST' \
      'http://localhost:8080/v1/clip/classify/cat/activity' \
      -H 'accept: application/json' \
      -F 'file=@./fixtures/scratching-cat.jpeg;type=image/jpeg' \
      -F 'labels=eating cat' \
      -F 'labels=grooming cat' \
      -F 'labels=scratching cat' \
      -F 'labels=sleeping cat'

[group("develop")]
up *args="":
  @docker compose up {{args}}

[group("develop")]
attach:
  @docker exec -it catiy-ml-catiy_ml-1 /bin/bash