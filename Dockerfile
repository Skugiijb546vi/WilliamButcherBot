FROM python:3.10-slim

WORKDIR /app

# دابەزاندنی پێداویستییەکان
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# دابەزاندنی uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ناچارکردنی بەکارهێنانی پایتۆنی ناو سێرڤەر
ENV UV_PYTHON_PREFERENCE=only-system

COPY . .

# دابەزاندنی کتێبخانەکان بەبێ بەکارهێنانی فایلی lock ی کۆن
RUN uv sync --no-dev --python 3.10

# ڕێڕەوی کارکردن
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
