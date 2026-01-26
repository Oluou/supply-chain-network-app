FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Security Best Practices
# 1. Do not hardcode secrets in Dockerfiles. Use environment variables or secret managers.
# 2. Avoid exposing sensitive ports to the public internet.
# 3. Use minimal base images and keep dependencies up to date.
# 4. Remove build tools and caches after installation to reduce image size and attack surface.
# 5. Set proper file permissions for application code and config files.
# 6. Use multi-stage builds for frontend to avoid leaking source code in production images.
