FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .

# لێرەدا دەمارە تێکچووەکە دەبڕین: بێدەنگکردنی ئەو بەشەی داوای ژمارەی مۆبایل دەکات
RUN sed -i 's/app2.start()/# app2.start()/g' wbb/__init__.py

RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"
CMD ["python", "-m", "wbb"]
