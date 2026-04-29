FROM python:3.10-slim-bullseye

# دیاریکردنی شوێنی کارکردن
WORKDIR /app

# دابەزاندنی پێداویستییە سەرەکییەکانی سێرڤەر
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# دابەزاندنی uv کە بۆتەکە پێویستی پێیەتی
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# کۆپیکردنی فایلەکان بۆ ناو سێرڤەر
COPY . .

# ئامادەکردنی کتێبخانەکان بە ڤێرژنی 3.10
RUN uv sync --frozen --no-dev --python 3.10

# ئیشپێکردنی بۆتەکە بە پایتۆنی 3.10 بۆ ئەوەی کراش نەکات
CMD ["uv", "run", "--python", "3.10", "python", "-m", "wbb"]
