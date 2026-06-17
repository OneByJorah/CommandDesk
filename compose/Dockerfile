FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# system deps for common wheels / networking
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# python deps
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

# app
COPY ticket_platforms /app/ticket_platforms
COPY memory_setup.py /app/memory_setup.py

EXPOSE 8000
CMD ["python", "-m", "ticket_platforms.registry"]
