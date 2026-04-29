FROM python:3.10-slim

WORKDIR /app

# دابەزاندنی پێداویستییەکان
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# دابەزاندنی uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# ناچارکردنی uv بۆ ئەوەی تەنها پایتۆنی ناو سێرڤەرەکە بەکاربهێنێت
ENV UV_PYTHON_PREFERENCE=only-system

COPY . .

# دابەزاندنی کتێبخانەکان بەبێ دابەزاندنی پایتۆنی نوێ
RUN uv sync --frozen --no-dev

# دڵنیابوونەوە لە ڕێڕەوی پایتۆن
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
