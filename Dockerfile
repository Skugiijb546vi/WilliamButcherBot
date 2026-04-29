FROM python:3.10-slim-bullseye
WORKDIR /app
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .
RUN uv sync --frozen --no-dev
ENV ENV=True
CMD ["uv", "run", "python", "-m", "wbb"]
