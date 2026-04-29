FROM python:3.10-slim-bullseye

WORKDIR /app

# دابەزاندنی پێداویستییەکان
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# هێنانە ناوەوەی uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

# *** لێرەدا ناچاری دەکەین تەنها پایتۆنی 3.10 بەکاربهێنێت ***
RUN uv sync --frozen --no-dev --python 3.10

# دڵنیابوونەوە لەوەی بۆتەکە ژینگەی پایتۆنی 3.10 بەکاردێنێت
ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "-m", "wbb"]
