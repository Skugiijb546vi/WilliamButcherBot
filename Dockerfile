FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .
RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"
# زیادکردنی PYTHONPATH بۆ ئەوەی پایتۆن فۆڵدەرەکان بناسێتەوە
ENV PYTHONPATH="/app"
# ئیشپێکردنی بۆتەکە بە فایلی سەرەکی نەک بە -m
CMD python3 -m wbb & python3 -m http.server 8080
