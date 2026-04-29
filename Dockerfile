FROM python:3.10-slim-bullseye

WORKDIR /wbb

RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

RUN uv sync --frozen --no-dev

# دڵنیابوونەوە لەوەی پایتۆن ڤێرژنی 3.10 بەکاردێنێت بۆ ئەوەی کراش نەکات
CMD ["uv", "run", "python", "-m", "wbb"]
