# syntax=docker/dockerfile:1
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /code

# Install dependencies first (leverages Docker cache)
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . .

# Expose default port (Railway automatically maps this)
EXPOSE 8080

# Run with Gunicorn using dynamic PORT for Railway / Docker Compose
CMD ["sh", "-c", "gunicorn run:app --bind 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 60"]
