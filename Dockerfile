FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY . .

# لێرەدا فێڵ لە ڕێندەر دەکەین بۆ ئەوەی بڵێین پۆرتمان هەیە
EXPOSE 8080

RUN uv sync --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# ئیشپێکردنی بۆتەکە بە جۆرێک کە ڕێندەر نەیکوژێت
CMD python3 -m wbb & python3 -m http.server 8080
