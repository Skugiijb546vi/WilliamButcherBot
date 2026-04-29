FROM python:3.10-slim

WORKDIR /app

# install system dependencies
RUN apt-get update && apt-get install -y git gcc build-essential && rm -rf /var/lib/apt/lists/*

# install nest-asyncio (ئەمە ئەو پاترییەیە کە بۆتەکە پێویستییەتی)
RUN pip install --no-cache-dir nest-asyncio aiohttp==3.8.6

COPY . .

# فێڵە گەورەکە: لێرەدا بە دەستی خۆمان 'هەناسە' دەدەین بە بۆتەکە
RUN sed -i '1i import nest_asyncio; nest_asyncio.apply()' wbb/__init__.py

# دابەزاندنی هەموو پێداویستییەکانی تر
RUN pip install --no-cache-dir -e .

# ئیشپێکردنی ڕاستەوخۆ
CMD ["python3", "-m", "wbb"]
