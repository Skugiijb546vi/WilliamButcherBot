FROM python:3.10-slim

WORKDIR /app

# install dependencies
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

# *** نه‌شته‌رگه‌ری لێره‌دایه‌: گۆڕینی مەرجی ڤێرژن لەناو فایلەکەدا ***
RUN sed -i 's/requires-python = ">=3.12"/requires-python = ">=3.10"/' pyproject.toml

# sync with python 3.10
RUN uv sync --no-dev --python 3.10

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
