FROM python:3.14

RUN apt -y update
RUN apt -y install libopencv-dev



# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

# Run the application.
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8080"]