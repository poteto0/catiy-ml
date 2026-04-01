FROM python:3.14

RUN apt -y update
RUN apt -y install libopencv-dev

# Install uv.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Copy the application into the container.
COPY . /app

# Install the application dependencies.
WORKDIR /app
RUN uv sync --locked --no-cache

# Run the application.
CMD ["/app/.venv/bin/fastapi", "run", "app/main.py", "--port", "80"]