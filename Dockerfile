# ============= BASE STAGE =============
# بەکارهێنانی پایتۆن 3.10 بۆ ئەوەی هەم uv ئیش بکات و هەم ئێرۆری لووپ نەمێنێت
FROM python:3.10-slim-bullseye AS base

WORKDIR /wbb

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# install required system dependencies
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    git gcc build-essential \
    iputils-ping \
    && rm -rf /var/lib/apt/lists/*

# install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

ENV PATH="/root/.local/bin/:$PATH"

# لێرەدا فایلی ڤێرژنمان سڕییەوە بۆ ئەوەی ناچار نەبێت 3.12 بەکاربهێنێت
COPY pyproject.toml .
COPY uv.lock .

# ============= PRODUCTION STAGE =============
FROM base

ENV UV_NO_DEV=1
# ئەم دێڕە ناچار دەکات بە پایتۆنی 3.10 ئیش بکات
RUN uv sync --python 3.10

COPY . .

# Starting Bot
ENTRYPOINT ["uv", "run", "--python", "3.10", "python", "-m", "wbb"]
