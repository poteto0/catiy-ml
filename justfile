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
ci: fmt lint check