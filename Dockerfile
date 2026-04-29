FROM python:3.10-slim

WORKDIR /app

# دابەزاندنی پێداویستییەکان
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# دابەزاندنی uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ناچارکردنی uv بۆ بەکارهێنانی پایتۆنی 3.10
ENV UV_PYTHON=python3.10
ENV UV_PYTHON_PREFERENCE=only-managed

COPY . .

# دابەزاندنی کتێبخانەکان بە قوفڵکراوی لەسەر 3.10
RUN uv sync --frozen --no-dev --python 3.10

# دڵنیابوونەوە لە ڕێڕەوی پایتۆن
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
