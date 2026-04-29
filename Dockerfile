FROM python:3.10-slim

WORKDIR /app

# install dependencies
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

# 1. گۆڕینی ڤێرژنی پایتۆن لەناو فایلەکاندا
RUN sed -i 's/requires-python = ">=3.12"/requires-python = ">=3.10"/' pyproject.toml

# 2. فێڵە گەورەکە: ناچارکردنی کۆدەکە بۆ دروستکردنی Event Loop لە سەرەتای کارکردندا
RUN sed -i '1s/^/import asyncio; asyncio.set_event_loop(asyncio.new_event_loop())\n/' wbb/__init__.py

# 3. دابەزاندنی کتێبخانەکان
RUN uv sync --no-dev --python 3.10

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
