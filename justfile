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
  @ENV=TEST uv run pytest --cov --cov-report=xml --cov-report=term

[group("ci")]
ut:
  @ENV=TEST uv run pytest

[group("ci")]
ci: fmt lint check ut

[group("ci")]
ci-check: fmt-check lint check ut

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
up *args="":
  @docker compose up {{args}}

[group("develop")]
attach:
  @docker exec -it catiy-ml-catiy_ml-1 /bin/bash